from pydantic import BaseModel, Field
from typing import Optional, List
from Models.Product import Product

class Cart(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	user_id: str
	items: List[Product]