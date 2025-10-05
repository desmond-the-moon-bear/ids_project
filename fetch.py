import io, numpy as np, pandas as pd, requests, streamlit as st

REPO = "https://raw.githubusercontent.com/desmond-the-moon-bear/ids_project/main/"

@st.cache_data
def fetch_np(path):
    response = requests.get(REPO + path)
    response.raise_for_status()
    return np.load(io.BytesIO(response.content))

