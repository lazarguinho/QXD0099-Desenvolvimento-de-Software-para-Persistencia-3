from pydantic import BaseModel, Field
from typing import Optional

class Category(BaseModel):
	id: Optional[str] = Field(None, alias='_id')
	name: str
	description: str
	status: str
	category_level: int
# id
# nome
# descricao
# status
# nivel_categoria