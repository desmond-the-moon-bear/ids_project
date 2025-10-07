import numpy as np
import pandas as pd
import random as rng
import streamlit as st

from runner import ScaledRunner
import fetch, rec

MINUTE_MS = 60 * 1000
STEP = 0.3

BUCKETS = [(i * MINUTE_MS, (i + STEP) * MINUTE_MS) for i in np.arange(0.75, 7, STEP)]
OFFSET = 0.4
BUCKETS_OFFSET = [b[0] * OFFSET for b in BUCKETS]


SONGS = "summary/songs_merged.csv"
ARTISTS = "summary/artists.csv"

@st.cache_data
def load_songs():
    songs = pd.read_csv(fetch.REPO + SONGS)
    songs.index = songs["song_id"]
    uri_to_id = dict(zip(songs["uri"], songs["song_id"].astype(int)))
    del songs["song_id"]
    return uri_to_id, songs

@st.cache_data
def load_artists(): return pd.read_csv(fetch.REPO + ARTISTS);

def make_buckets(songs: pd.DataFrame):
    buckets = []
    for bounds in BUCKETS:
        bucket = songs[songs["duration_ms"] >= bounds[0]]
        bucket = songs[songs["duration_ms"] <  bounds[1]]
        buckets.append(bucket)
    return buckets

def make_target_bpm(current_duration, function: ScaledRunner):
    targets = []
    for offset in BUCKETS_OFFSET:
        targets.append(function(current_duration + offset))
    return targets

def filter_buckets_by_targets(buckets, targets, bpm_error):
    filtered_buckets = []
    for i in range(0, len(targets)):
        filtered_bucket = buckets[i]
        filtered_bucket = filtered_bucket[filtered_bucket["bpm"] > (targets[i] - bpm_error)]
        filtered_bucket = filtered_bucket[filtered_bucket["bpm"] < (targets[i] + bpm_error)]
        filtered_buckets.append(filtered_bucket)
    return filtered_buckets

def choose_song(buckets):
    song_count = 0
    for bucket in buckets:
        song_count += len(bucket)
    if song_count == 0: return pd.DataFrame()
    song_index = rng.randrange(song_count)
    for bucket in buckets:
        if song_index < len(bucket): return bucket.iloc[[song_index]];
        else: song_index -= len(bucket);
    return pd.DataFrame()

MAX_ITERATIONS = 300
GAP_PERCENTAGE = 0.003
def generate_playlist(source_playlist, bpm_error, function: ScaledRunner, K: int = 100):
    with st.spinner("Fetching data...", show_time=True):
        if isinstance(source_playlist, bool):
            if source_playlist: uri_to_id, songs = load_songs()
            else: return False, None
        else:
            uri_to_id, songs = load_songs()
            recs = rec.make_recommendations(source_playlist, uri_to_id, K=K)
            if recs: songs = songs.loc[recs]
            else: return False, None
        artists = load_artists()

    with st.spinner("Generating playlist...", show_time=True):
        buckets = make_buckets(songs)

        if function.duration < 1000:
            function.duration *= MINUTE_MS;

        current_duration = 0
        result = []
        iter = 0
        chosen_songs = set()
        while current_duration < function.duration:
            targets = make_target_bpm(current_duration, function)
            filtered_buckets = filter_buckets_by_targets(buckets, targets, bpm_error)
            song = choose_song(filtered_buckets)
            if len(song) > 0:
                if not song["uri"].iloc[0] in chosen_songs:
                    current_duration += song["duration_ms"].iloc[0]
                    result.append(song)
                    chosen_songs.add(song["uri"].iloc[0])
            else: break;
            iter += 1
            if iter > MAX_ITERATIONS: break;

        status = "ok"
        if current_duration < function.duration: status = "partial"

        if function.duration > 1000:
            function.duration /= MINUTE_MS;

        if not result: return False, None
        result = pd.concat(result, ignore_index=True)
        result["duration"] = result["duration_ms"] / MINUTE_MS
        result["x1"] = result["duration"].cumsum()
        result["x1"] = result["x1"] - function.duration * GAP_PERCENTAGE
        result["x0"] = result["x1"].shift(fill_value=0)
        result["x0"] = result["x0"] + function.duration * GAP_PERCENTAGE
        result["artist"] = result["artist"].map(lambda index: artists["name"].iloc[index])
        result = result.rename(columns={"name": "Title", "artist": "Artist"})

    return status, result
