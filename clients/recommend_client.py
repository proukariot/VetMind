import requests
from clients.consts import SERVER_URL


def get_recommendation(interview_description, treatment_description):

    payload = {
        "interview_description": interview_description,
        "treatment_description": treatment_description,
    }
    api_url = f"{SERVER_URL}/get_recommendation"
    response = requests.post(api_url, json=payload)
    response.raise_for_status()
    return response.json()
