import streamlit as st
import numpy as np, pandas as pd, faiss
import fetch

IDS = "model/emb_song_ids.npy"
EMB = "model/embeddings.npy"

@st.cache_resource
def load_model():
    ids = fetch.fetch_np(IDS).astype(np.int64)
    emb = fetch.fetch_np(EMB).astype(np.float32) # L2-normalized

    # quick look-up from song ID to row
    id_to_row = {int(s): i for i, s in enumerate(ids)}

    # HNSWF is an approximate nearest-neighbour structure (ANN)
    # Organizes points in a multi-layer graph so queries quickly
    # walk the graph rather than compare against every vector.
    index = faiss.IndexHNSWFlat(emb.shape[1], 32)
    # how thoroughly the graph is built, when higher value it considers
    # more candidates while inserting a node, better graph quality
    index.hnsw.efConstruction = 80 
    # with higher value the search explores a larger candidate set
    # before picking the top-k, higher recall, higher latency
    index.hnsw.efSearch = 64 
    # adds all vectors to the index
    index.add(emb) 

    return ids, emb, id_to_row, index

# Given one or more seed songs, fuse their neighbor lists into K
# recommendations using Reciprocal Rank Fusion (RRF) prefers items that are
# consistently high-ranked across provided seeds per_seed_fetch overfetches to
# have enough unique candidates.
def recommend_multi_rrf(
        ids, emb, id_to_row, index,
        seeds_song_ids, K: int, per_seed_fetch: int = 300, k0: float = 60.0
    ):
    seeds = [int(s) for s in (seeds_song_ids if isinstance(seeds_song_ids,(list,tuple)) else [seeds_song_ids])]
    seed_rows = [id_to_row[s] for s in seeds if s in id_to_row]
    if not seed_rows: return []

    L = max(per_seed_fetch, K*3) # how many neighbours to ask per seed
    seed_set = set(seed_rows)
    lists = []
    for r in seed_rows:
        D, I = index.search(emb[r:r+1], L + 1)
        cand = [j for j in I[0].tolist() if j != r]
        lists.append([j for j in cand if j not in seed_set])

    if not any(lists): return []

    cand = np.unique(np.concatenate([np.array(lst, dtype=np.int32) for lst in lists])) # unique candidates
    rrf = np.zeros(cand.size, dtype=np.float32)
    for lst in lists:
        pos = {int(j): p+1 for p, j in enumerate(lst)}      # rank 1 = best
        ranks = np.array([pos.get(int(j), 10**9) for j in cand], dtype=np.int64)
        m = ranks < 10**9
        rrf[m] += 1.0 / (k0 + ranks[m])

    top = np.argpartition(rrf, -min(K, rrf.size))[-min(K, rrf.size):]
    top = top[np.argsort(rrf[top])[::-1]]
    return ids[cand[top]].astype(int).tolist()

def make_recommendations(source_playlist, uri_to_id):
    with st.spinner("Making recommendations...", time=True):
        try:
            playlist = pd.read_csv(source_playlist)
            uris = playlist['Spotify - id'].to_list()
        except: return []
        ids, emb, id_to_row, index = load_model()
        seed_ids = [uri_to_id[uri] for uri in uris if uri in uri_to_id]
        if seed_ids: return recommend_multi_rrf(ids, emb, id_to_row, index, seed_ids, K=100)
        else: return []
