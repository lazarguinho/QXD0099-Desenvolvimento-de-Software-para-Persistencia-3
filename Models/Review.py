from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Review(BaseModel):
    id: Optional[str] = Field(None, alias='_id')
    nota: int
    comentario: str
    data: datetime = Field(default_factory=lambda: datetime.now(datetime.timezone.utc))
    titulo: str
    status: str = Field(choices=["pendente", "aprovado", "rejeitado"])

    user_id: str
    product_id: str