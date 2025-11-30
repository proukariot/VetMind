# TODO fix
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import os
import json
import datetime

from clients.recommend_client import get_recommendation
from llm.transcription import transcribe_audio, save_transcription
from llm.ai import summarize_vet_visit
from clients.sql_client import get_animals


# -----------------------------------------------------------
# 🌟 Wyróżniony nagłówek aplikacji
# -----------------------------------------------------------

st.markdown(
    """
    <h1 style="
        text-align: center; 
        color: #2458a6;
        font-size: 48px;
        margin-bottom: 10px;">
        🐾 Vet Assistant 💙
    </h1>
    <p style="text-align:center; color:#4a4a4a; margin-top:-10px;">
        Inteligentny asystent gabinetu weterynaryjnego
    </p>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------
# 🧠 Stan aplikacji
# -----------------------------------------------------------

if "transcription" not in st.session_state:
    st.session_state.transcription = None

if "summary" not in st.session_state:
    st.session_state.summary = None

# -----------------------------------------------------------
# 🐾 Dane o pacjencie
# -----------------------------------------------------------

animals_data = get_animals()
selected_animal = None
selected_owner = None
birth_year = None
age = None

st.markdown("## 🐶 Wybór pacjenta")

if not animals_data:
    st.error("Brak danych o zwierzętach z serwera.")
else:
    # Wybór właściciela
    owner_names = sorted(list({row["owner_name"] for row in animals_data}))
    selected_owner = st.selectbox(
        "Wybierz właściciela", owner_names, placeholder="Wybierz z listy"
    )

    # Zwierzęta danego właściciela
    animals_for_owner = [
        row for row in animals_data if row["owner_name"] == selected_owner
    ]

    if animals_for_owner:
        # Wybór zwierzęcia
        animal_name_to_obj = {row["pet_name"]: row for row in animals_for_owner}
        selected_animal_name = st.selectbox(
            "Wybierz zwierzę",
            list(animal_name_to_obj.keys()),
            placeholder="Wybierz pacjenta",
        )

        selected_animal = animal_name_to_obj.get(selected_animal_name)

        # --- Karta pacjenta ---
        if selected_animal:
            st.markdown("---")
            st.subheader("📋 Karta pacjenta")

            current_year = datetime.datetime.now().year
            birth_year = int(selected_animal["birth_year"])
            age = current_year - birth_year

            st.markdown(f"### 🐾 {selected_animal['pet_name']}")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Opiekun:**", selected_owner)
                st.write("**Gatunek:**", selected_animal["species"].capitalize())
                st.write("**Rasa:**", selected_animal["breed"])
                st.write("**Płeć:**", selected_animal["sex"].capitalize())

            with col2:
                st.write("**Wiek:**", f"{age} lat")
                st.write("**Rok urodzenia:**", f"{birth_year}")
                st.write("**Umaszczenie:**", selected_animal["coat"])
                st.write("**Waga:**", f"{selected_animal['waga']} kg")
    else:
        st.info("Wybrany opiekun nie ma jeszcze dodanych zwierząt w systemie.")

# -----------------------------------------------------------
# 🎙️ Sekcja nagrywania
# -----------------------------------------------------------

st.markdown("---")
st.markdown(
    """
    <div style="
        margin-top: 10px;
        padding: 18px;
        border-radius: 12px;
        border: 2px solid #6ab0ff;
        background-color: #eef6ff;">
        <h3 style="margin-top: 0;">🎙️ Nagrywanie wizyty</h3>
        <p style="margin: 0;">Nagraj rozmowę z opiekunem, a asystent automatycznie przygotuje notatkę z wizyty.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

SAVE_DIR = "Recordings"
TRANS_DIR = "Transcriptions"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(TRANS_DIR, exist_ok=True)

audio_file = st.audio_input("Kliknij, aby rozpocząć nagrywanie")

# Przycisk do ręcznego uruchamiania transkrypcji
process_button = st.button("🔄 Przetwórz nagranie", disabled=audio_file is None)

if audio_file is None:
    st.caption(
        "Najpierw nagraj lub wgraj plik audio, a następnie kliknij „Przetwórz nagranie”."
    )

if process_button:
    if audio_file is None:
        st.warning("Najpierw nagraj lub wybierz plik audio.")
    elif selected_animal is None:
        st.warning(
            "Najpierw wybierz pacjenta, aby powiązać nagranie z właściwym zwierzęciem."
        )
    else:
        # Podgląd nagrania
        st.audio(audio_file)

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        animal_id = selected_animal["id_animal"] if selected_animal else "unknown"
        audio_filename = f"recording_{animal_id}_{timestamp}.wav"
        audio_path = os.path.join(SAVE_DIR, audio_filename)

        # Zapis nagrania
        with open(audio_path, "wb") as f:
            f.write(audio_file.getvalue())

        # Reset poprzednich wyników
        st.session_state.transcription = None
        st.session_state.summary = None

        # -----------------------------------------------------------
        # 🔄 Transkrypcja + AI (nowy pipeline)
        # -----------------------------------------------------------
        with st.spinner("Przetwarzam nagranie (transkrypcja + analiza)..."):
            try:
                # transcribe_audio powinno zwrócić dict z polami raw/cleaned
                transcription_json = transcribe_audio(audio_path)

                # Zapis transkrypcji do katalogu Transcriptions
                save_transcription(transcription_json, output_dir=TRANS_DIR)

                st.session_state.transcription = transcription_json

                st.success("📝 Transkrypcja została zapisana i powiązana z wizytą.")

                # Używamy oczyszczonej transkrypcji, jeśli jest dostępna
                tekst_do_podsumowania = (
                    transcription_json.get("cleaned_transcription")
                    or transcription_json.get("raw_transcription")
                    or ""
                )

                if tekst_do_podsumowania.strip():
                    summary = summarize_vet_visit(tekst_do_podsumowania)
                    st.session_state.summary = summary
                else:
                    st.warning(
                        "Transkrypcja jest pusta – nie udało się wygenerować podsumowania."
                    )

            except Exception as e:
                st.error(
                    "Wystąpił problem podczas transkrypcji lub generowania podsumowania."
                )
                st.caption(f"Szczegóły techniczne (dla developera): {e}")
                st.session_state.summary = None

# -----------------------------------------------------------
# 📜 Podgląd transkrypcji
# -----------------------------------------------------------

if st.session_state.transcription:
    t = st.session_state.transcription
    st.markdown("## 📜 Transkrypcja z wizyty")

    with st.expander("Pokaż transkrypcję"):
        st.markdown("#### Oczyszczona transkrypcja")
        st.write(t.get("cleaned_transcription", "_brak oczyszczonej transkrypcji_"))

        st.markdown("#### Surowa transkrypcja")
        st.write(t.get("raw_transcription", "_brak surowej transkrypcji_"))

        meta_cols = st.columns(3)
        with meta_cols[0]:
            st.caption(f"Plik źródłowy: `{t.get('source_file', 'brak')}`")
        with meta_cols[1]:
            st.caption(f"Język: {t.get('language', 'nieznany')}")
        with meta_cols[2]:
            st.caption(f"Utworzono: {t.get('created_at', 'brak daty')}")

# -----------------------------------------------------------
# 🧾 Ładnie sformatowane podsumowanie wizyty
# -----------------------------------------------------------

summary = st.session_state.summary

if summary:
    st.markdown("## 🧾 Podsumowanie wizyty")

    col_left, col_right = st.columns(2)

    # Lewa kolumna: objawy + czas trwania
    with col_left:
        st.markdown("### 🩺 Objawy")
        objawy = summary.get("objawy", [])
        if objawy:
            st.markdown(
                "<ul>" + "".join([f"<li>{o}</li>" for o in objawy]) + "</ul>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown("_nie podano_")

        st.markdown("### ⏱️ Od kiedy się dzieje")
        st.markdown(f"**{summary.get('od_kiedy_sie_dzieje', 'nie podano')}**")

    # Prawa kolumna: leki + dodatkowe informacje
    with col_right:
        st.markdown("### 💊 Przyjmowane leki")

        leki = summary.get("przyjmowane_leki", [])
        if leki:
            for med in leki:
                st.markdown(
                    f"""
                    <div style="padding: 8px 12px; background:#f7f7f7; border-radius:8px; margin-bottom:8px;">
                    <strong>{med.get('nazwa', 'nie podano')}</strong><br>
                    • dawka: {med.get('dawka', 'nie podano')}<br>
                    • częstotliwość: {med.get('czestotliwosc', 'nie podano')}<br>
                    • droga podania: {med.get('droga_podania', 'nie podano')}<br>
                    • uwagi: {med.get('dodatkowe_uwagi', 'nie podano')}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown("_nie podano_")

        st.markdown("### 📝 Dodatkowe informacje")
        st.markdown(f"**{summary.get('dodatkowe_informacje', 'nie podano')}**")

    st.caption("Automatycznie wygenerowane na podstawie nagranej rozmowy.")

    with st.spinner("Przetwarzam rekomendacje..."):
        try:
            # Rekomendowane leki
            st.markdown("### 💊 Rekomendowane leki")

            interview_description = ",".join(objawy)
            treatment_description = ",".join(leki)

            rag_recommendation_str = get_recommendation(
                interview_description, treatment_description
            )
            rag_recommendation = json.loads(rag_recommendation_str)
            rekomendowane_leki = rag_recommendation.get("leki", [])
            if rekomendowane_leki:
                for med in rekomendowane_leki:
                    st.markdown(
                        f"""
                        <div style="padding: 8px 12px; background:#e8f0fe; border-radius:8px; margin-bottom:8px;">
                        <strong>{med.get('nazwa', 'nie podano')}</strong><br>
                        • dawka: {med.get('dawka', 'nie podano')}<br>
                        • częstotliwość: {med.get('czestotliwosc', 'nie podano')}<br>
                        • droga podania: {med.get('droga_podania', 'nie podano')}<br>
                        • uwagi: {med.get('dodatkowe_uwagi', 'nie podano')}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown("_nie podano_")

            # Rekomendacje dotyczące leczenia
            st.markdown("### 🩺 Rekomendacje dotyczące leczenia")
            rekomendacje_terapia = rag_recommendation.get("zalecenia", "")
            if rekomendacje_terapia:
                # Łączymy elementy w jeden ciąg tekstu, oddzielony przecinkami
                st.markdown(f"**{rekomendacje_terapia}**")
            else:
                st.markdown("_nie podano_")

            st.caption(
                "Automatycznie wygenerowane na podstawie traskrypcji i historyi leczenia."
            )
        except Exception:
            st.error("Wystąpił problem podczas generowania rekomendacji.")

elif audio_file and process_button:
    # tylko jeśli dopiero co próbowaliśmy coś przetworzyć
    st.info("Brak podsumowania do wyświetlenia.")
