class DbClient:
    def get_animals_data(self) -> dict:
        raise NotImplementedError

    def write(self, key: str, value: dict) -> None:
        raise NotImplementedError


class SupabaseClient(DbClient):
    def __init__(self, supabase_url, supabase_key):
        # init Supabase
        ...

    def get_animals_data(self, key: str) -> dict:
        # reading
        ...

    def write(self, key: str, value: dict):
        # writing
        ...


class MockDbClient(DbClient):
    def __init__(self):
        self.store = {
            "animals": [
                {
                    "id_animal": 21,
                    "pet_name": "Kropka",
                    "breed": "border collie",
                    "sex": "samica",
                    "age": 2,
                    "birth_year": 2023,
                    "coat": "czarny, podpalany",
                    "weight": 16,
                    "owner_name": "Magdalena Nowak",
                    "species": "pies",
                },
            ]
        }

    def get_animals_data(self) -> dict:
        key = "animals"
        return self.store.get(key, {})

    def write(self, key: str, value: dict):
        self.store[key] = value
