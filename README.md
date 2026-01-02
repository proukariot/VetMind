#  VetMind — Pet Visit Demo Project

Project VetMind contains tools for make the veterinarian's job easier

The functionality is demonstrated on the Streamlit UI client


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

Configure the project with file `pyproject.toml`:

```bash
pip install -e . 
```
---


## Example Streamlit UI (client)

Inside `ui/` there's a Streamlit sample that shows a simple UI for using the extraction endpoints.

```bash
streamlit run src/ui/app.py
```
---

## Tests

TBA

---
 
## License

This project is licensed under the [MIT License](LICENSE).

## Authors
- Raman Bylina: raman.bylina@gmail.com
- Magdalena Sztuk: kimagdalenasztuk@gmail.com
- Uladzimir Karaliou: vova@bessia.net
- Stefan Marynowicz: marynowy4@gmail.com
- Mateusz Kaźmierczak: mateusz.z.kazmierczak@gmail.com
 