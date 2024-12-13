import requests

def invoke_authenticated_listings_api(payload: dict):
    response = requests.request(
        'POST',
        'https://realtime.oxylabs.io/v1/queries',
        auth=('YOUR_USERNAME', 'YOUR_PASSWORD'),  # Your credentials go here
        json=payload,
    )


def fetch_live_product_listings(search_term: str) -> list:
    ...


def fetch_listings_amazon(search_term: str) -> list:
    # Structure payload.
    payload = {
        'source': 'amazon_search',
        'user_agent_type': 'desktop_firefox',
        'query': search_term,
        'parse': True,
        'start_page': 1,

    }
