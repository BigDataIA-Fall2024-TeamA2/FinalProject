from fastapi import APIRouter, Depends

from backend.schemas.search import SearchRequest
from backend.services.auth_bearer import get_current_user_id
from backend.services.search import process_initial_search_query

search_router = APIRouter(prefix="/search", tags=["search"])


@search_router.post(
    "/initial",
)
async def initial_search(
    request: SearchRequest, user_id: int = Depends(get_current_user_id)
):
    return await process_initial_search_query()

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
