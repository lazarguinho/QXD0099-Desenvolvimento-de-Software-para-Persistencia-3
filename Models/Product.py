from pydantic import BaseModel, Field
from typing import Optional, List
from Models.Category import Category

class Product(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    name: str
    description: str
    price: float
    stock_quantity: int
    categories: List[Category]