
# VetMind — Pet Visit Demo Project

This folder contains the Hackathon_DzikiAI project — a collection of demo components that focus on extracting structured medical visit data from text and PDFs using LLMs, exposing a FastAPI backend, and simple client / UI examples (including a Streamlit UI and an iOS sample).


---

## Contents

- `server/` — FastAPI server that provides LLM and SQL operations 
- `clients/` — Python clients for the server API (e.g., `extract_client.py`).
- `llm/` — Utilities for LLM operations (eg. Whisper transcription helper) and example code.
- `ui/` — Simple Streamlit UI (`ui/app.py`) 
- `tests/` — Example scripts that demonstrate the API usage and basic integration tests.
- `schemas/` — Pydantic models used by the server (e.g., `Visit`).
- `requirements.txt` — Python dependencies used by the project.
- `.env` — Example or local env used for tests or Docker runs

---

## Requirements

- Python 3.11+ (recommended)
- pip
- Docker & Docker Compose (optional for Docker workflows)

Install requirements:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file with the variables needed for the server and tests, for example:

```
OPENAI_API_KEY=your_openai_key
MODEL=gpt-4.1
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
```

Keep your keys private and don’t commit `.env` to the repository. Consider adding `.env.template` listing the required keys.

---


## Server as Docker Container

1) Build the Docker image (from repo root):

```bash
docker build -f server/Dockerfile -t pet-extractor .
```

2) Run the image with an `.env` file:

```bash
docker run -p 8000:8000 --env-file .env pet-extractor
```

The server is then available on http://localhost:8000. API docs are available at http://localhost:8000/docs.
More information in [How to run the server with Docker](server/HOW_TO_RUN_SERVER.md)

2) Endpoints:

- `GET /` — health check
- `POST /extract` — body: `{ "text": "..." }` — use LLM for extract structed visit data from a raw text
- `POST /extract_pdf` — extract the data from PDF
- `POST /add_visit` — add a visit to Supabase DB 
- `GET /visits` — return visits list from Supabase
- `GET /animals` — return animals list from Supabase

Example curl:

```bash
curl -X POST http://localhost:8000/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Patient: Burek, species: dog, age: 7..."}'
```


Configure `clients/consts.py` to point to `SERVER_URL` if the server runs on a different address than `http://localhost:8000`.

---

## Example Streamlit UI (client)

Inside `ui/` there's a Streamlit sample that shows a simple UI for using the extraction endpoints.

```bash
streamlit run ui/app.py
```

---

## Tests

Test scripts exist in `tests/`:

```bash
python tests/test_extract_client.py
python tests/test_sql_client.py
```

They demonstrate reading a PDF, sending text to the `/extract` endpoint, and using `clients/sql_client` to test database interactions.

To run a more thorough test suite, convert these scripts to `pytest` format and follow normal `pytest` flows.

---
 

 
## License

This project is licensed under the [MIT License](LICENSE).

## Authors
- Raman Bylina: raman.bylina@gmail.com
- Magdalena Sztuk: kimagdalenasztuk@gmail.com
- Uladzimir Karaliou: vova@bessia.net
- Stefan Marynowicz: marynowy4@gmail.com
- Mateusz Kaźmierczak: mateusz.z.kazmierczak@gmail.com
 
