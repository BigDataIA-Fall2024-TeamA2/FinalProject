from pydantic import BaseModel

class SearchQuery(BaseModel):
    query: str

class Product(BaseModel):
    title: str
    price: str
    product_url: str
    merchant_name: str
