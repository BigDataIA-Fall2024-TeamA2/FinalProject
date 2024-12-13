from fastapi import APIRouter, HTTPException
from typing import List
from backend.schemas.product import SearchQuery, Product
from backend.ecom.fetchlistings import fetch_google_shopping_results, extract_product_details

router = APIRouter()

@router.post("/search", response_model=List[Product])
def search_products(query: SearchQuery):
    api_response = fetch_google_shopping_results(query.query)
    if not api_response:
        raise HTTPException(status_code=500, detail="Error fetching data from API")
    products = extract_product_details(api_response)
    return products
