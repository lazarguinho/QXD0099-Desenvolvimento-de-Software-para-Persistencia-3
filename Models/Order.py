from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Order(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	date: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
	status: str = Field(choices=['pendente', 'pago', 'enviado', 'entregue', 'cancelado'])
	total: float
	payment_method: str
	delivery_price: float

	user_id: str
	items: List[str]