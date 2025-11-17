import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

from database import create_document, get_documents, db

app = FastAPI(title="Clothing Brand API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductIn(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image: Optional[str] = Field(None, description="Image URL")
    tag: Optional[str] = Field(None, description="Badge like 'New' or 'Sale'")


def serialize_doc(doc: dict) -> dict:
    d = {**doc}
    _id = d.get("_id")
    if isinstance(_id, ObjectId):
        d["id"] = str(_id)
        del d["_id"]
    return d


@app.get("/")
def read_root():
    return {"message": "Clothing Brand API is running"}


@app.get("/api/products", response_model=List[dict])
def list_products(category: Optional[str] = None):
    filter_q = {"category": category} if category else {}
    docs = get_documents("product", filter_q, limit=None)
    return [serialize_doc(d) for d in docs]


@app.post("/api/products", status_code=201)
def create_product(product: ProductIn):
    try:
        new_id = create_document("product", product)
        return {"id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/categories", response_model=List[str])
def get_categories():
    try:
        names = db["product"].distinct("category") if db else []
        return names
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/seed", summary="Seed sample products if collection is empty")
def seed_products():
    try:
        count = db["product"].count_documents({}) if db else 0
        if count > 0:
            return {"status": "ok", "message": "Products already exist", "count": count}
        samples = [
            {
                "title": "Essential Tee",
                "description": "Ultra-soft cotton tee with a relaxed fit.",
                "price": 29.0,
                "category": "Tops",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1520975922224-c3b61545d0f3?q=80&w=1400&auto=format&fit=crop",
                "tag": "New"
            },
            {
                "title": "Classic Hoodie",
                "description": "Cozy fleece hoodie for everyday comfort.",
                "price": 59.0,
                "category": "Outerwear",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1520974735194-5f2d45c7c6b3?q=80&w=1400&auto=format&fit=crop",
                "tag": "Bestseller"
            },
            {
                "title": "Slim Fit Jeans",
                "description": "Stretch denim with a modern slim silhouette.",
                "price": 79.0,
                "category": "Bottoms",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1516826957135-700dedea698c?q=80&w=1400&auto=format&fit=crop",
                "tag": ""
            },
            {
                "title": "Athletic Joggers",
                "description": "Lightweight joggers designed for movement.",
                "price": 49.0,
                "category": "Bottoms",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1519741497674-611481863552?q=80&w=1400&auto=format&fit=crop",
                "tag": "Limited"
            },
            {
                "title": "Everyday Cap",
                "description": "Minimal cap with adjustable strap.",
                "price": 25.0,
                "category": "Accessories",
                "in_stock": True,
                "image": "https://images.unsplash.com/photo-1592878904946-b3cd5f0775c7?q=80&w=1400&auto=format&fit=crop",
                "tag": ""
            },
        ]
        for s in samples:
            create_document("product", s)
        return {"status": "ok", "inserted": len(samples)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
