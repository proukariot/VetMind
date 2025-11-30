# TODO fix
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


from llm.transcription import transcribe_audio

PATH = "data/recording_1.wav"


if __name__ == "__main__":
    transcription_json = transcribe_audio(PATH)

    print(transcription_json)
