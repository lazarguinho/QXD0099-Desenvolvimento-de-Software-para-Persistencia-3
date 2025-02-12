from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Cart(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	data_criacao: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
	subtotal: float
	quantidade_items: int
	status: str = Field(choices=['pendente', 'pago', 'enviado', 'entregue', 'cancelado'])
	
	items: Optional[List[str]] = []