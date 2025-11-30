import json
import datetime
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI()

POLISH_VET_PROMPT = """
Jesteś modelem do lekkiego czyszczenia transkrypcji rozmów z wizyt u weterynarza.

ZASADY KRYTYCZNE — MUSISZ ICH BEZLITOŚNIE PRZESTRZEGAĆ:
1. NIE WOLNO dodawać żadnych informacji, których nie ma w nagraniu.
2. NIE WOLNO dopowiadać porad, diagnoz, wyjaśnień ani opisów medycznych.
3. NIE WOLNO rozszerzać krótkich wypowiedzi – jeśli w surowej transkrypcji jest jedno zdanie, wynik też jest jednym zdaniem.
4. NIE WOLNO zmieniać sensu ani treści wypowiedzi.
5. Możesz poprawiać jedynie:
   - literówki,
   - interpunkcję,
   - oczywiste błędy językowe,
   - usuwać „yyy”, „eee”, „no”, „wie pan”, „wie pani”.
6. Styl i długość wypowiedzi musi pozostać jak najbliżej oryginału.
7. Jeśli surowy tekst jest bardzo krótki (“A gorączkę”), NIE ROZWIJASZ GO.

Twoja odpowiedź to wyłącznie delikatnie oczyszczony tekst.
Nic więcej.
"""


def _clean_transcription(raw_text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": POLISH_VET_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def transcribe_audio(file_path: str) -> dict:
    """
    Pełny pipeline:
    - Whisper → raw
    - GPT → cleaned
    """

    # === WHISPER ===
    with open(file_path, "rb") as f:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", file=f, language="pl"
        )

    raw_text = transcription.text
    cleaned_text = _clean_transcription(raw_text)

    now = datetime.datetime.now()

    return {
        "created_at": now.isoformat(),
        "source_file": os.path.basename(file_path),
        "type": "wizyta_weterynaryjna",
        "language": "pl",
        "raw_transcription": raw_text,
        "cleaned_transcription": cleaned_text,
    }


def save_transcription(
    transcription_json: dict, output_dir: str = "Transcriptions"
) -> str:
    """
    Zapisuje cały obiekt transkrypcji do JSON.
    """
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"transcription_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(transcription_json, f, ensure_ascii=False, indent=2)

    return filepath
