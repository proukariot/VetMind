# TODO fix
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from clients.extract_client import extract_visit_text
from pypdf import PdfReader
import json


PDF_PATH = "data/Walker.pdf"


def read_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


if __name__ == "__main__":
    print("✔ Reading PDF...")
    pdf_text = read_pdf(PDF_PATH)

    print("✔ Sending to API...")
    result = extract_visit_text(pdf_text)

    print("\n✔ Result JSON:")
    print(json.dumps(result, indent=4, ensure_ascii=False))
