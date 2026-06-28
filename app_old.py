import streamlit as st
import pandas as pd
import os

from core.scoring import score_job

# =========================================================
# CONFIG
# =========================================================

DATA_PATH = "data/jobs.csv"

st.set_page_config(
    page_title="RIA Executive OS — Intelligence Dashboard",
    layout="wide"
)

st.title("🧠 RIA Executive OS — Market Intelligence Engine")

st.write("""
Pipeline-driven architecture:

✔ Offline job ingestion  
✔ Scoring engine (RIA OS-aligned)  
✔ Intelligence dashboard for executive targeting
""")

# =========================================================
# LOAD DATA
# =========================================================

if not os.path.exists(DATA_PATH):
    st.error(f"Missing data file: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)

required_cols = ["title", "company"]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"Missing required columns: {missing}")
    st.stop()

# =========================================================
# SCORE DATA
# =========================================================

df["score"] = df.apply(score_job, axis=1)
df = df.sort_values("score", ascending=False)

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("Filters")

min_score = st.sidebar.slider(
    "Minimum Fit Score",
    0, 100, 50
)

companies = st.sidebar.multiselect(
    "Company",
    options=sorted(df["company"].dropna().unique())
)

title_search = st.sidebar.text_input("Search Job Title")

# Apply filters
filtered = df[df["score"] >= min_score]

if companies:
    filtered = filtered[filtered["company"].isin(companies)]

if title_search:
    filtered = filtered[
        filtered["title"].str.contains(title_search, case=False, na=False)
    ]

# =========================================================
# EXECUTIVE SNAPSHOT
# =========================================================

st.subheader("📊 Market Snapshot")

col1, col2, col3 = st.columns(3)

col1.metric("Total Jobs", len(df))
col2.metric("Filtered Jobs", len(filtered))
col3.metric(
    "Avg Fit Score",
    round(filtered["score"].mean(), 1) if len(filtered) else 0
)

# =========================================================
# TOP OPPORTUNITIES
# =========================================================

st.subheader("🔥 Top Opportunities")

top_n = st.slider("Show Top N Jobs", 5, 50, 15)

st.dataframe(
    filtered.head(top_n)[["title", "company", "score"]],
    use_container_width=True
)

# =========================================================
# JOB DETAIL EXPLORER
# =========================================================

st.subheader("🔎 Job Explorer")

if len(filtered) > 0:

    selected_idx = st.selectbox(
        "Select Job",
        options=filtered.index,
        format_func=lambda i: f"{filtered.loc[i, 'title']} — {filtered.loc[i, 'company']}"
    )

    job = filtered.loc[selected_idx]

    st.markdown(f"""
    ## {job['title']}
    **Company:** {job['company']}  
    **Score:** {job['score']}
    """)

    if "location" in job:
        st.write("**Location:**", job.get("location"))

    if "description" in job:
        st.write("**Description:**", job.get("description"))

    if "url" in job:
        st.write("**URL:**", job.get("url"))
else:
    st.warning("No jobs match your filters.")
