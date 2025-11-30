# TODO fix
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from clients.sql_client import get_animals, send_visit
from schemas.visit import Visit


def test_send_visit():
    visit = Visit(
        id_animal=1,
        owner_name="Jan Nowak",
        pet_name="Burek",
        breed="mieszany",
        species="pies",
        age=7,
        sex="samiec",
        coat="rudy",
        weight="10",
        interview_description="opis_wywiadu",
        treatment_description="opis_badania",
        applied_medicines="zastosowane leki",
        recommendation="zalecenia",
    )
    send_visit(visit)


if __name__ == "__main__":
    # visit = get_test_visit()
    a = get_animals()
    print(f"animals: {a}")
    # send_visit(visit)
