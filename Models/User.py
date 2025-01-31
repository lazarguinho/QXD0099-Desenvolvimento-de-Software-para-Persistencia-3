from pydantic import BaseModel, Field
from typing import Optional, List

class User(BaseModel):
	id: Optional[int] = Field(None, alias='_id')
	name: str
	email: str
	password: str
	address: str
	phoneNumber: str