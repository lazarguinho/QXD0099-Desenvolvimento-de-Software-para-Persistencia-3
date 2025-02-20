from pydantic import BaseModel, Field
from typing import Optional, List

class Product(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    name: str
    description: str
    price: float
    stock_quantity: int
    
    category_id: str
    carts: Optional[List[str]] = []