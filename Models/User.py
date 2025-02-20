from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	name: str
	email: str
	password: str
	address: str
	phoneNumber: str

	carrinho_id: Optional[str] = Field(None, alias='carrinho_id')
	pedidos: Optional[List[str]] = []
