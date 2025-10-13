import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

import runner as run
import solver

st.set_page_config(
    page_title="RhythmRun – Personalized Workout Playlists", layout="wide")

indigo = "#332288"
cyan = "#88ccee"
teal = "#44aa99"
green = "#117733"
olive = "#999933"
sand = "#ddcc77"
rose = "#cc6677"
wine = "#882255"
purple = "#aa4499"
pale_grey = "#dddddd"

OI_BLUE = "#0072B2"
OI_SKY = "#56B4E9"
OI_SKY_t = "#5193B9CE"
OI_GREEN = "#009E73"
OI_BLACK = "#000000"
OI_GREY = "#7A7A7A"
BG_LIGHT = "#F3F6FA"
CARD_BG = "#FFFFFF"


st.markdown(f"""
<style>
.block-container {{
  max-width: 100vw !important;
  padding: 1rem 1vw 2rem 1vw !important;
  box-shadow: none !important;
  border: none !important;
}}

html, body, [data-testid="stAppViewContainer"] {{
  background: radial-gradient(circle at 10% 0%, {OI_SKY}22 0%, transparent 45%),
              linear-gradient(180deg, {OI_SKY}11, var(--background-color));
}}

.rr-hero {{
  width: 100%;
  margin: 2rem 0 1rem 0;
  background: {OI_SKY_t};
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.16);
  border-radius: 26px;
  padding: 2rem 1rem;
  text-align: center;
  display: flex; align-items: center; 
  justify-content: center; text-align: center;
}}

.rr-hero h1 {{
  margin: 0;
  font-weight: 800;
  letter-spacing: .3px;
  color: #ffffff; /* Light mode */
}}

@media (prefers-color-scheme: dark) {{
  .rr-hero h1 {{
    color: {OI_BLACK}; /* Dark mode */
  }}
}}

/* Floating cards */
[data-testid="stVerticalBlockBorderWrapper"] {{
  background: var(--secondary-background-color) !important;
  border: 1px solid rgba(0,0,0,.002) !important;
  border-radius: 22px !important;
  box-shadow: 0 12px 30px {OI_SKY}22;
}}

/* Typography */
.section-title {{
  position: relative;
  font-size: 1.55rem; font-weight: 800; color: {OI_BLUE}; margin-bottom: .6rem;
}}
.section-title:after {{
  content: ""; position: absolute; left: 0; bottom: -6px; height: 4px; width: 82px;
  border-radius: 999px;
  background: linear-gradient(90deg, {wine}, {OI_SKY});
}}
.subtle {{ color: var(--text-color-secondary); }}
label, .stSlider label, .stFileUploader label {{ font-weight: 700 !important; color: var(--text-color) !important; }}

/* BUTTONS  */
div.stButton > button,
.stDownloadButton > button,
[data-testid="stLinkButton"] > a,
[data-testid="stLinkButton"] > a[role="button"],
[data-testid="stLinkButton"] button {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-width: 160px;
  padding: 0 16px;
  height: 44px;
  border-radius: 14px !important;
  font-weight: 800;
  letter-spacing: .3px;
  background: {OI_BLUE} !important;
  color: #fff !important;
  border: none !important;
  text-decoration: none !important;
  box-shadow: 0 8px 22px {OI_BLUE} 44;
  transition: transform .06s ease, color .15s ease, background .15s ease, box-shadow .15s ease, filter .15s ease;
}}

/* Hover state */
div.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stLinkButton"] > a:hover,
[data-testid="stLinkButton"] button:hover {{
  background: {OI_BLUE} !important;
  color: {wine} !important;
  box-shadow: 0 8px 22px {wine} 44;
  filter: brightness(1.02);
}}

/* Pressed */
div.stButton > button:active,
.stDownloadButton > button:active,
[data-testid="stLinkButton"] > a:active {{
  background: {wine} !important;
  color: #fff !important;
}}

/* Sliders */

.stSlider [role="slider"] {{
  background: {wine} !important;
  border: 2px solid {wine} !important;
  color: {wine} !important;
}}
.stSlider .st-emotion-cache-16idsys, .stSlider .st-emotion-cache-1fcdlhc {{
  background: {OI_BLUE}22 !important;
}}

/* Info boxes */
[data-baseweb="notification"] {{
  margin: 0.5rem 0 0.5rem 0;
  border-radius: 14px; background: {OI_SKY}15;
  border: 1px solid {OI_SKY}55;
  color: {OI_BLUE} !important;
}}

/* Links */
a, .markdown-text-container a {{ color: {wine}; }}
a:hover {{ filter: brightness(0.95); }}

/* Tables */
.stTable {{
  margin-top: 0.5rem; 
}}
.stTable thead tr th {{
  background: {OI_SKY}20 !important; color: {OI_BLUE} !important; font-weight: 800 !important;
  border-bottom: 2px solid {wine}33 !important;
}}
.stTable tbody tr td {{ padding: .6rem .8rem !important; }}

/* Table column widths */
.stTable thead tr th {{
  white-space: nowrap !important;
  padding: 0.6rem 1rem !important;
}}

.stTable tbody tr td {{
  white-space: nowrap !important;
  padding: 0.6rem 1rem !important;
}}

.stTable th:nth-child(3),
.stTable td:nth-child(3) {{
  min-width: 80px !important; /* BPM column */
  text-align: center;
}}

.stTable th:nth-child(4),
.stTable td:nth-child(4) {{
  min-width: 90px !important; /* Duration column */
  text-align: center;
}}


<style>
""", unsafe_allow_html=True)

st.markdown('<div class="rr-hero"><h1>RhythmRun – Personalized Workout Playlists</h1></div>',
            unsafe_allow_html=True)

if not 'status' in st.session_state:
    st.session_state.status = False

col_pref, col_vis, col_table = st.columns([0.8, 1.5, 1.5], gap="small")


# COLUMN 1 — Preferences

with col_pref:
    with st.container(border=True):
        st.markdown(
            "<div class='section-title'>Your Preferences</div>", unsafe_allow_html=True)
        st.caption(
            "Upload a seed playlist and adjust the workout curve. The curve updates live as you slide.")
        source_playlist = st.file_uploader(
            "Upload a playlist (CSV)", type=["csv"],
            help="Seed playlist; URIs/IDs are used to anchor the generated set."
        )

        MIN_BPM = 65
        max_bpm = st.slider(
            "Max Intensity", 90, 190, 170,
            help="Peak BPM target (height of the plateau). Raises the whole curve proportionally."
        )
        duration = st.slider(
            "Run Duration (Minutes)", 5.0, 60.0, 30.0,
            help="Total workout length. Stretches or compresses the curve along the time (x) axis."
        )
        climb = st.slider(
            "Climb Smoothstep", 0, 6, 3,
            help="Controls ramp-up smoothness. Higher = longer rise with a sudden increase; lower = less change in acceleration."
        )
        descent = st.slider(
            "Descent Smoothstep", 0, 6, 3,
            help="Controls cool-down smoothness. Higher = longer descent with a sharp drop; lower = more gradual drop."
        )
        min_climb = st.slider(
            "Start Intensity %", 0, 100, 30,
            help="Starting intensity as % of Max. Sets the baseline at time 0 (e.g., warm-up level)."
        )
        min_descent = st.slider(
            "Stop Intensity %", 0, 100, 35,
            help="Ending intensity as % of Max. Sets the final cool-down floor near the end."
        )
        max_start = st.slider(
            "Climb Stop %", 0, 100, 40,
            help="Point in workout (0–100%) where the climb reaches Max intensity (end of ramp-up)."
        )
        max_stop = st.slider(
            "Descent Start %", 0, 100, 100,
            help="Point in workout (0–100%) where the descent begins (start of cool-down)."
        )
        error = st.slider("BPM Error", 1, 20,
            help="How much a song can differ from the BPM sampled from the curve."
        )
        max_stop = max(max_stop, max_start)

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

        function_x_scale = alt.Scale(domain=[0, float(run_function.duration)])
        y_scale = alt.Scale(domain=[0, 250])

        input = np.arange(0.001, duration, 0.002 * duration)
        output = run_function_vec(input)
        line = pd.DataFrame({
            "x": input,
            "y": output
        })

        if st.button("Generate", use_container_width=True):
            st.session_state.status, st.session_state.playlist = \
            solver.try_generate_playlist(
                source_playlist if source_playlist is not None else True,
                error,
                run_function,
            )
            if not st.session_state.status:
                st.warning(
                    "Not enough suggestions to generate playlist. Increase\
                    BPM Error for better results. Changing the intensity function\
                    may also yield better results.")

        if st.button("Clear", use_container_width=True):
            st.session_state.status = False
            st.session_state.pop("playlist", None)


# COLUMN 2 — Visualizations

with col_vis:
    with st.container(border=True):
        st.markdown("<div class='section-title'>Visualizations</div>",
                    unsafe_allow_html=True)
        st.markdown("<div class='subtle'>Workout BPM Curve</div>",
                    unsafe_allow_html=True)

        line_chart = (
            alt.Chart(line).mark_line().encode(
                x=alt.X("x", title="Time", scale=function_x_scale),
                y=alt.Y("y", title="BPM",  scale=y_scale),
            ).configure_mark(
                color=wine,
                strokeWidth=5
            )
        )
        st.altair_chart(line_chart, key="line_chart", use_container_width=True)

        st.markdown("<div class='subtle'>Workout Timeline</div>",
                    unsafe_allow_html=True)

        if st.session_state.status != False:
            if st.session_state.status == "partial":
                st.warning("Not enough suggestions to generate a full playlist. Increase\
                    BPM Error for better results. Changing the intensity function\
                    may also yield better results.")

            playlist = st.session_state.playlist
            x_scale = alt.Scale(domain=[0, playlist["duration"].sum()])
            single_selection = alt.selection_point()
            chart = (
                alt.Chart(playlist)
                .mark_rect(
                    cornerRadiusTopLeft=5,
                    cornerRadiusTopRight=5,
                    stroke=None
                )
                .encode(
                    x=alt.X("x0", type="quantitative",
                            title="Time", scale=x_scale),
                    x2="x1",
                    y=alt.Y("bpm", type="quantitative",
                            title="BPM", scale=y_scale),
                    tooltip=["Title", "Artist"],
                    color=alt.condition(
                        single_selection,
                        alt.value(wine),
                        alt.value(wine)
                    ),
                    fillOpacity=alt.condition(
                        single_selection,
                        alt.value(1),
                        alt.value(0.3)
                    )
                )
                .add_params(single_selection)
                .properties(spacing=5)
            )

            event = st.altair_chart(
                chart, key="playlist_chart", on_select="rerun", use_container_width=True)
            if event and len(event.selection.param_1) > 0:
                x0 = event.selection.param_1[0]["x0"]
                song_df = playlist[playlist["x0"] == x0].iloc[0]
                url_text = f"{song_df['Title']} by {song_df['Artist']}"
                url = f"https://open.spotify.com/track/{song_df['uri']}"
                st.link_button(url_text, url, use_container_width=True)
        else:
            st.info("Generate a playlist to see the workout timeline.")


# COLUMN 3 — Generated Playlist

with col_table:
    with st.container(border=True):
        st.markdown(
            "<div class='section-title'>Generated Playlist</div>", unsafe_allow_html=True)

        if st.session_state.status != False:
            playlist_df = playlist[["Title", "Album", "Artist", "bpm", "duration"]]
            playlist_df.index = range(1, len(playlist_df)+1)
            st.table(playlist_df)

            @st.cache_data
            def convert_for_download(playlist: pd.DataFrame):
                return playlist["uri"].to_csv(index=False).encode("utf-8")

            csv = convert_for_download(playlist)
            st.download_button(
                label="Download",
                data=csv,
                file_name="playlist.csv",
                mime="text/csv",
                icon=":material/download:",
                use_container_width=True,
            )
        else:
            st.info(
                "Your generated playlist will appear here once you click **Generate**.")
