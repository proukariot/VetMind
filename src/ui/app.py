import os
import datetime
import streamlit as st

import clients.audio_processing as audio_processing
import clients.db_client as db_client
import ui_consts
from utils.i18n import t


db_client = db_client.MockDbClient()
audio_processing_client = audio_processing.AutoLangAudioTranscriptionClient()


# -----------------------------
# Init
# -----------------------------
def init():
    os.makedirs(ui_consts.SAVE_DIR, exist_ok=True)
    os.makedirs(ui_consts.TRANS_DIR, exist_ok=True)


# -----------------------------
# UI rendering functions
# -----------------------------
def render_header():
    """Render the main header of the app."""
    st.markdown(
        f"<h1 style='text-align:center; color:#2458a6'>{t('header.title')}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align:center; color:#4a4a4a'>{t('header.subtitle')}</p>",
        unsafe_allow_html=True,
    )


def select_language():
    """Language selection sidebar."""
    lang = st.sidebar.selectbox(
        t("header.select_language"),
        options=["pl", "en", "ru"],
        index=["pl", "en", "ru"].index(
            st.session_state.get("lang", ui_consts.DEFAULT_LANGUAGE)
        ),
    )
    st.session_state.lang = lang


def render_patient_card(animal, owner):
    """Render the detailed patient info card."""
    st.markdown("---")
    st.subheader(t("patient.card_title"))

    current_year = datetime.datetime.now().year
    birth_year = int(animal["birth_year"])
    age = current_year - birth_year

    st.markdown(f"### 🐾 {animal['pet_name']}")

    col1, col2 = st.columns(2)
    with col1:
        st.write("**Owner:**", owner)
        st.write(f"**{t('patient.species')}:**", animal["species"].capitalize())
        st.write(f"**{t('patient.breed')}:**", animal["breed"])
        st.write(f"**{t('patient.sex')}:**", animal["sex"].capitalize())
    with col2:
        st.write(f"**{t('patient.age')}:**", f"{age} {t('patient.years')}")
        st.write(f"**{t('patient.birth_year')}:**", birth_year)
        st.write(f"**{t('patient.coat')}:**", animal["coat"])
        st.write(f"**{t('patient.weight')}:**", f"{animal['weight']} kg")


def render_patient_selection():
    """Display patient selection and return the selected animal and owner."""
    st.markdown("## " + t("patient.card_title"))
    animals_data = db_client.get_animals_data()
    selected_animal = None
    selected_owner = None

    if not animals_data:
        st.error(t("errors.no_animals_data"))
        return selected_animal, selected_owner

    owner_names = sorted(list({row["owner_name"] for row in animals_data}))
    selected_owner = st.selectbox(t("patient.select_owner"), owner_names)

    animals_for_owner = [
        row for row in animals_data if row["owner_name"] == selected_owner
    ]

    if not animals_for_owner:
        st.info(t("errors.no_animals_for_owner"))
        return selected_animal, selected_owner

    animal_name_to_obj = {row["pet_name"]: row for row in animals_for_owner}
    selected_animal_name = st.selectbox(
        t("patient.select_animal"), list(animal_name_to_obj.keys())
    )
    selected_animal = animal_name_to_obj.get(selected_animal_name)

    if selected_animal:
        render_patient_card(selected_animal, selected_owner)

    return selected_animal, selected_owner


def save_audio(audio_file, animal_id):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    audio_filename = f"recording_{animal_id}_{timestamp}.wav"
    audio_path = os.path.join(ui_consts.SAVE_DIR, audio_filename)

    with open(audio_path, "wb") as f:
        f.write(audio_file.getvalue())
    return audio_path


# TODO refactor: it's needed to be split into two functions
def render_audio_section(selected_animal):
    """Render the audio recording widget and handle processing."""
    st.markdown("---")
    st.markdown(
        f"<div style='margin-top:10px;padding:18px;border-radius:12px;border:2px solid #6ab0ff;background-color:#eef6ff;'>"
        f"<h3 style='margin-top:0'>{t('recording.title')}</h3>"
        f"<p style='margin:0'>{t('recording.description')}</p></div>",
        unsafe_allow_html=True,
    )

    audio_file = st.audio_input(t("recording.audio_input"))
    process_button = st.button(
        t("recording.process_button"), disabled=audio_file is None
    )

    if audio_file is None:
        st.caption(t("errors.no_audio"))
        return None

    animal_id = selected_animal["id_animal"] if selected_animal else "unknown"
    audio_path = save_audio(audio_file, animal_id)

    transcribed = None
    if process_button:
        transcribed = audio_processing_client.transcript(audio_path)
    return transcribed


def render_transcription_text(text: str):
    """Render transcription text block."""
    print(f"text: {text}")

    if not text:
        return

    with st.expander(t("transcription.title")):
        st.markdown(f"**{t('transcription.raw')}**")
        st.write(text)


# -----------------------------
# Main function
# -----------------------------
def main():
    init()
    select_language()
    render_header()
    selected_animal, selected_owner = render_patient_selection()
    transcribed_text = render_audio_section(selected_animal)
    render_transcription_text(transcribed_text)


if __name__ == "__main__":
    main()
