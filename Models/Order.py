from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class OrderStatus(str, Enum):
	PENDING = "pending"
	PAID = "paid"
	SHIPPED = "shipped"
	DELIVERED = "delivered"
	CANCELLED = "cancelled"

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    price: float

class Order(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	items: List[OrderItem]
	tracking_number: Optional[str] = None