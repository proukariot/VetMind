from pydantic import BaseModel


class Visit(BaseModel):
    id_animal: int
    owner_name: str
    species: str
    pet_name: str
    breed: str
    sex: str
    coat: str
    age: float
    weight: float
    interview_description: str
    treatment_description: str
    applied_medicines: str
    recommendation: str

    def get_payload(self):
        return {
            "id_animal": self.id_animal,
            "owner_name": self.owner_name,
            "species": self.species,
            "pet_name": self.pet_name,
            "breed": self.breed,
            "sex": self.sex,
            "coat": self.coat,
            "age" : self.age,
            "weight": self.weight,
            "interview_description": self.interview_description,
            "treatment_description": self.treatment_description,
            "applied_medicines": self.applied_medicines,
            "recommendation": self.recommendation,
        }
