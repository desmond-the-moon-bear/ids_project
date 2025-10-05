import io, numpy as np, pandas as pd, requests, streamlit as st

REPO = "https://raw.githubusercontent.com/desmond-the-moon-bear/ids_project/main/"
REPO_LFS = "https://media.githubusercontent.com/media/desmond-the-moon-bear/ids_project/refs/heads/main/"

@st.cache_data
def fetch_np(path):
    response = requests.get(REPO_LFS + path)
    response.raise_for_status()
    return np.load(io.BytesIO(response.content))

