from pydantic import BaseModel, Field
from typing import Optional

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
    image: Optional[str] = Field(None, description="Image URL")
    tag: Optional[str] = Field(None, description="Badge like 'New' or 'Sale'")
