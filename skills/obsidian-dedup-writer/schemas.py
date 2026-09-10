"""VLM 输出强类型。"""
from pydantic import BaseModel, Field


class CardJSON(BaseModel):
    name: str = Field(min_length=1)
    company: str = ""
    role: str = ""
    phones: list[str] = Field(default_factory=list)
    emails: list[str] = Field(default_factory=list)
    city: str = ""
    product_hint: str = ""
