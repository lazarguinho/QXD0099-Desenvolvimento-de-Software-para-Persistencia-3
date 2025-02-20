from pydantic import BaseModel, Field
from typing import List, Optional

class Category(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	name: str
	description: str
	status: str
	category_level: str

	products: List[str]