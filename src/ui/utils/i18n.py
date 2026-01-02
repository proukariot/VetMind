import yaml
import streamlit as st
from functools import lru_cache
import os

import ui_consts

LOCALE_DIR = os.path.join(os.path.dirname(__file__), "..", "locale")


@lru_cache
def load_locales():
    langs = {}
    for code in ["pl", "en", "ru"]:
        path = os.path.join(LOCALE_DIR, f"{code}.yml")
        with open(path, "r", encoding="utf-8") as f:
            langs[code] = yaml.safe_load(f)
    return langs


def t(key: str) -> str:
    lang = st.session_state.get("lang", ui_consts.DEFAULT_LANGUAGE)
    parts = key.split(".")
    node = load_locales()[lang]
    for p in parts:
        node = node.get(p, {})
    if isinstance(node, dict):
        return f"[MISSING:{key}]"
    return node
