import requests
from schemas.visit import Visit
from clients.consts import SERVER_URL


def send_visit(visit: Visit):
    payload = visit.get_payload()
    print(payload)
    r = requests.post(f"{SERVER_URL}/add_visit", json=payload)
    print("Response:", r.json())
    print("Response code:", r.status_code)


def get_visits():
    r = requests.get(f"{SERVER_URL}/visits")
    return r.json()


def get_animals():
    r = requests.get(f"{SERVER_URL}/animals")
    return r.json()
