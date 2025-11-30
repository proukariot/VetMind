import json
import os
from io import BytesIO

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse

from pydantic import BaseModel
from dotenv import load_dotenv
from pypdf import PdfReader
import openai
from transcriber import transcribe_audio

from supabase import create_client, Client

from schemas.visit import Visit
from llm.rag.vector_db import get_recommendations


# -----------------------
# Config
# -----------------------
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("MODEL", "gpt-4.1")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="Pet Medical Extraction API",
    description="API for extracting medical data from text/PDF and working with visits in Supabase.",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc docs
    openapi_url="/openapi.json",
)


# ============================================================
# 🟦 LLM PART – TEXT & PDF EXTRACTION
# ============================================================


class TextInput(BaseModel):
    text: str


class RecommendationRequest(BaseModel):
    interview_description: str
    treatment_description: str


def build_prompt(text: str) -> str:
    # Build prompt for medical data extraction
    return f"""
Przetwórz poniższy tekst i zwróć wynik w formacie JSON o strukturze:
{{
    "pet_name": "",
    "breed": "",
    "sex": "",
    "age": "",
    "coat": "",
    "weight": "",
    "interview_description": "",
    "treatment_description": "",
    "applied_medicines": "",
    "recommendation": ""
}}

Tekst źródłowy:
----------------
{text}
"""


def extract_from_text(text: str) -> dict:
    # Call OpenAI to extract structured data
    prompt = build_prompt(text)

    response = openai.chat.completions.create(
        model=MODEL,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "Jesteś asystentem do ekstrakcji danych medycznych o zwierzętach.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    data = json.loads(response.choices[0].message.content)
    return data


def read_pdf_bytes(pdf_bytes: bytes) -> str:
    # Read PDF from bytes and return its extracted text
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text


@app.post("/extract", tags=["LLM"])
async def extract_info(payload: TextInput):
    """
    LLM: Extract structured data from plain text.
    """
    return extract_from_text(payload.text)


@app.post("/extract_pdf", tags=["LLM"])
async def extract_info_from_pdf(file: UploadFile = File(...)):
    """
    LLM: Extract structured data from uploaded PDF file.
    """
    pdf_bytes = await file.read()
    pdf_text = read_pdf_bytes(pdf_bytes)
    return extract_from_text(pdf_text)


@app.post("/get_recommendation", tags=["LLM"])
async def get_recommendation(request: RecommendationRequest):
    """
    LLM: Get recommendation with RAG
    """
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    rec_data = get_recommendations(
        request.interview_description,
        request.treatment_description,
        api_key=OPENAI_API_KEY,
    )
    return rec_data


app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/transcribe")
async def transcribe_endpoint(file: UploadFile = File(...)):
    """
    Przyjmuje plik audio i zwraca transkrypcję JSON.
    """
    try:
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(await file.read())

        result = transcribe_audio(filepath)

        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ============================================================
# 🟩 SQL PART – SUPABASE DATABASE OPERATIONS
# ============================================================


@app.post("/add_visit", tags=["SQL"])
def add_visit(visit: Visit):
    """
    SQL: Insert new visit into Supabase.
    """
    payload = visit.get_payload()
    result = supabase.table("visits").insert(payload).execute()
    return {"status": "ok", "data": result.data}


@app.get("/visits", tags=["SQL"])
def get_all_visits():
    """
    SQL: Get all visits.
    """
    result = supabase.table("visits").select("*").order("id_visit", desc=True).execute()
    return result.data


@app.get("/animals", tags=["SQL"])
def get_all_animals():
    """
    SQL: Get all animals.
    """
    result = (
        supabase.table("animals").select("*").order("id_animal", desc=True).execute()
    )
    return result.data


# ============================================================
# 🟧 HEALTH CHECK
# ============================================================


@app.get("/", tags=["Health"])
def health():
    return {"status": "ok"}
