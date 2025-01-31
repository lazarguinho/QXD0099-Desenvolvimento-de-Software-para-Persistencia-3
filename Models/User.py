from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	name: str
	email: str
	password: str
	address: str
	phoneNumber: str