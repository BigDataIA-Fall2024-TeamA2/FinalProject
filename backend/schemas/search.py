from pydantic import BaseModel, field_validator

from backend.services.choices import get_supported_product_categories


class SearchRequest(BaseModel):
    model: str
    prompt: str
    category: str

    @field_validator('category')
    @classmethod
    def _cat_supported(cls, v: str) -> str:
        if v not in get_supported_product_categories():
            raise ValueError(f"{v} is not a supported product category.")
        return v
