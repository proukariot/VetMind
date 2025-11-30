import faiss
import numpy as np
from tqdm import tqdm
import openai
import json
from openai import OpenAI
import pickle


from llm.rag.rag_consts import *


def get_embedding(client, text):
    response = client.embeddings.create(model=EMBEDDING_MODEL_NAME, input=text)

    return np.array(response.data[0].embedding, dtype=np.float32)


def get_visit_text(visit):
    visit_text = f"{visit['interview_description']} {visit['treatment_description']}"
    return visit_text


def process_visits(client, visits):
    embedding_list = []
    id_to_visit = []
    for visit in tqdm(visits):
        visit_text = get_visit_text(visit)
        emb = get_embedding(client, visit_text)
        embedding_list.append(emb)
        id_to_visit.append(visit["id_visit"])
    return embedding_list, id_to_visit


def build_index(embedding_list):
    embeddings_array = np.vstack(embedding_list)
    dimension = embeddings_array.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_array)

    print(f"Added {len(embeddings_array)} vectors.")
    return index


def find_in_vector_db(
    interview_description, treatment_description, k, client, loaded_index
):
    # Tworzymy embedding dla zapytania
    query_text = f"{interview_description}  {treatment_description}"
    query_vector = get_embedding(client, query_text).reshape(1, -1)

    # Wyszukujemy najbliższe przypadki w bazie FAISS
    distances, indices = loaded_index.search(query_vector, k=k)
    return distances, indices


def get_similar_visits_info(indices, visits, loaded_id_to_visit):
    # Zbieramy leki i zalecenia z najbliższych wizyt
    similar_visits_info = []
    for idx in indices[0]:
        visit_id = loaded_id_to_visit[idx]
        visit = next(v for v in visits if v["id_visit"] == visit_id)
        similar_visits_info.append(
            {
                "applied_medicines": visit["applied_medicines"],
                "recommendation": visit["recommendation"],
            }
        )
    return similar_visits_info


def generate_prompt_for_new_visit(
    interview_description,
    treatment_description,
    k,
    visits,
    client,
    loaded_index,
    loaded_id_to_visit,
):
    """
    Generuje prompt dla nowej wizyty na podstawie podobnych przypadków w bazie.

    ```
    Parametry:
    - interview_description: tekst wywiadu pacjenta
    - treatment_description: opis leczenia
    - k: liczba najbliższych przypadków do uwzględnienia
    """
    distances, indices = find_in_vector_db(
        interview_description, treatment_description, k, client, loaded_index
    )

    similar_visits_info = get_similar_visits_info(indices, visits, loaded_id_to_visit)

    # Tworzymy prompt dla LLM z informacjami o podobnych przypadkach
    prompt = f"Nowa wizyta:\nWywiad: {interview_description}\nLeczenie: {treatment_description}\n\nPodobne przypadki i ich zalecenia:\n"
    for i, info in enumerate(similar_visits_info, 1):
        prompt += f"{i}. Leki: {info['applied_medicines']}, Zalecenia: {info['recommendation']}\n"

    prompt += "\nNa podstawie tych przykładów, wygeneruj zalecenia i przepisz leki dla nowej wizyty."

    return prompt


def get_recommendations_inner(
    rec_model,
    interview_description,
    treatment_description,
    k,
    visits,
    client,
    loaded_index,
    loaded_id_to_visit,
):
    prompt = generate_prompt_for_new_visit(
        interview_description,
        treatment_description,
        k,
        visits,
        client,
        loaded_index,
        loaded_id_to_visit,
    )

    prompt += "\n\nProszę odpowiedzieć wyłącznie w formacie JSON."

    response = openai.chat.completions.create(
        model=rec_model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "Jesteś asystentem do rekomendacji poleceń medycznych dla zwierząt.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    # response_format=json_object возвращает готовый Python объект
    data = response.choices[0].message.content
    return data


def init(api_key):
    k = DEFAULT_K
    visits = []
    with open(VISITS_FILENAME, "r", encoding="utf-8") as f:
        visits = json.load(f)

    client = OpenAI(api_key=api_key)
    loaded_index = faiss.read_index(INDEX_FILENAME)
    with open(ID_TO_VISIT_FILENAME, "rb") as f:
        loaded_id_to_visit = pickle.load(f)

    return k, visits, client, loaded_index, loaded_id_to_visit


def get_recommendations(interview_description, treatment_description, api_key):
    rec_model = RECOMMENDATION_MODEL_NAME
    k, visits, client, loaded_index, loaded_id_to_visit = init(api_key)
    rec_data = get_recommendations_inner(
        rec_model,
        interview_description,
        treatment_description,
        k,
        visits,
        client,
        loaded_index,
        loaded_id_to_visit,
    )
    return rec_data
