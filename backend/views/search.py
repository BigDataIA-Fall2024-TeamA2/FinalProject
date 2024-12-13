from fastapi import APIRouter, Depends, HTTPException

from backend.schemas.search import SearchRequest, Product, SearchQuery
from backend.services.auth_bearer import get_current_user_id
from backend.services.search import process_initial_search_query, fetch_google_shopping_results, extract_product_details


search_router = APIRouter(prefix="/search", tags=["search"])


@search_router.post("/product-listings", response_model=list[Product])
def search_products(query: SearchQuery):
    api_response = fetch_google_shopping_results(query.query)
    if not api_response:
        raise HTTPException(status_code=500, detail="Error fetching data from API")
    products = extract_product_details(api_response)
    return products


@search_router.post(
    "/initial",
)
async def initial_search(
    request: SearchRequest, user_id: int = Depends(get_current_user_id)
):
    return await process_initial_search_query(request.model, request.prompt, request.category, user_id)

"""
    Initial Search -> List[Products]
    
    Product:
        name: Sony MX4  -> Oxxylabs API
        review summary
        
    ProductL:
        name: Sony MZ3  -> Oxxylabs API
        review summary
        
    
    Refined Search -> 
"""
