import requests
from clients.consts import SERVER_URL


def extract_visit_text(text):
    payload = {"text": text}
    api_url = f"{SERVER_URL}/extract"
    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    return response.json()
