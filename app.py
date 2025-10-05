import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import runner as run
import solver

st.set_page_config(layout="wide")

indigo    = "#332288"
cyan      = "#88ccee"
teal      = "#44aa99"
green     = "#117733"
olive     = "#999933"
sand      = "#ddcc77"
rose      = "#cc6677"
wine      = "#882255"
purple    = "#aa4499"

if not 'generated' in st.session_state:
    st.session_state.generated = False

MIN_BPM = 50
max_bpm     = st.slider("Max Intensity",          90,  230)
duration    = st.slider("Run Duration (Minutes)", 5.0, 60.0)
climb       = st.slider("Climb Smoothstep",       0,   6)
descent     = st.slider("Descent Smoothstep",     0,   6)
min_climb   = st.slider("Start Intensity %",      0,   100)
min_descent = st.slider("Stop Intensity %",       0,   100)
max_start   = st.slider("Climb Stop %",           0,   100)
max_stop    = st.slider("Descent Start %",        0,   100, 100);
max_stop    = max(max_stop, max_start)

run_function = run.ScaledRunner(
    max_bpm,
    duration,
    climb, descent,
    max(min_climb / 100, MIN_BPM / max_bpm),
    max(min_descent / 100, MIN_BPM / max_bpm),
    max_start / 100,
    max_stop / 100
)
run_function_vec = np.vectorize(run_function)

function_x_scale = alt.Scale(domain=[0, run_function.duration])
y_scale = alt.Scale(domain=[0, 250])

input  = np.arange(0.001, duration, 0.002 * duration)
output = run_function_vec(input)
line = pd.DataFrame({
    "x": input,
    "y": output,
})
line_chart = (
    alt.Chart(line).mark_line().encode(
        x = alt.X("x", title="Time", scale=function_x_scale),
        y = alt.Y("y", title="BPM", scale=y_scale),
    ).configure_mark(
        color=wine,
        strokeWidth=5
    )
)

st.altair_chart(line_chart, key = "line_chart")

source_playlist = st.file_uploader("Choose a playlist", type="csv")

if st.button("Generate"):
    st.session_state.generated = True
    st.session_state.playlist = solver.generate_playlist(
        source_playlist if source_playlist is not None else True,
        1, run_function
    )

if st.button("Clear"):
    st.session_state.generated = False

@st.cache_data
def convert_for_download(playlist: pd.DataFrame):
    return playlist["uri"].to_csv(index=False).encode("utf-8")

if st.session_state.generated:
    playlist = st.session_state.playlist
    x_scale = alt.Scale(domain=[0, playlist["duration"].sum()])
    single_selection = alt.selection_point()
    chart = (
        alt.Chart(playlist).mark_rect(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
            x  = alt.X("x0", type="quantitative", title="Time", scale=x_scale),
            x2 = "x1",
            y  = alt.Y("bpm", type="quantitative", title="BPM", scale=y_scale),
            tooltip = ["Title", "Artist"],
            color = alt.condition(single_selection, alt.value(cyan), alt.value(teal)),
            fillOpacity = alt.condition(single_selection, alt.value(1), alt.value(0.5))
        ).add_params(single_selection)
    )

    csv = convert_for_download(playlist)
    st.download_button(
        label="Download",
        data=csv,
        file_name="playlist.csv",
        mime="text/csv",
        icon=":material/download:",
    )

    playlist_df = playlist[["Title", "Artist", "bpm", "duration"]]
    st.table(playlist_df)

    event = st.altair_chart(chart, key = "playlist_chart", on_select = "rerun")
    if event and len(event.selection.param_1) > 0:
        x0 = event.selection.param_1[0]["x0"]
        song_df = playlist[playlist["x0"] == x0].iloc[0]
        url_text = f"{song_df["Name"]} by {song_df["Artist"]}"
        url = f"https://open.spotify.com/track/{song_df["uri"]}"
        st.link_button(url_text, url, width="stretch")
