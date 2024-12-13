from typing import List, Dict

import requests

from backend.agent import agent_workflow
from backend.config import settings
from backend.schemas.search import InitialSearchResponse


async def process_initial_search_query(
    model: str, prompt: str, category: str, user_id: int
) -> InitialSearchResponse:
    response = agent_workflow.invoke({"prompt": prompt, "category": category})

    print(response["steps"])

    tools_used = ["vector_search"]
    if response.get("perform_web_search", False):
        tools_used.append("web_search")

    return InitialSearchResponse(
        response=response["generation"],
        tools_used=tools_used
    )

def fetch_google_shopping_results(search_term: str) -> Dict:
    payload = {
        'source': 'google_shopping_search',
        'domain': 'com',
        'query': search_term,
        'pages': 1,
        'parse': True,
    }
    try:
        response = requests.post(
            'https://realtime.oxylabs.io/v1/queries',
            auth=(settings.OXYLABS_USERNAME, settings.OXYLABS_PASSWORD),
            json=payload,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error invoking API: {e}")
        return {}

def extract_product_details(api_response: Dict) -> List[Dict]:
    products = []
    if not api_response or 'results' not in api_response:
        print("Invalid API response.")
        return products

    for result in api_response['results']:
        content = result.get('content', {})
        organic_results = content.get('results', {}).get('organic', [])

        for product in organic_results:
            product_id = product.get('product_id', 'N/A')
            title = product.get('title', 'N/A')
            price = product.get('price_str', 'N/A')
            merchant_info = product.get('merchant', {})
            merchant_name = merchant_info.get('name', 'N/A')

            product_url = f"https://www.google.com/shopping/product/{product_id}"

            products.append({
                'title': title,
                'price': price,
                'product_url': product_url,
                'merchant_name': merchant_name,
            })

    return products