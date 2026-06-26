import streamlit as st
import pandas as pd
import os

from core.scoring import score_job


DATA_PATH = "data/jobs.csv"


# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="RIA Executive OS — Intelligence Dashboard",
    layout="wide"
)

st.title("🧠 RIA Executive OS — Market Intelligence Engine")

st.write("""
Pipeline-driven architecture:

✔ Offline job ingestion (pipeline)  
✔ CSV-based persistence  
✔ Deterministic scoring engine  
✔ Stable Streamlit dashboard  
""")

# =========================================================
# LOAD DATA FROM PIPELINE
# =========================================================

@st.cache_data(ttl=60)
def load_jobs():

    if not os.path.exists(DATA_PATH):
        return pd.DataFrame()

    return pd.read_csv(DATA_PATH)


df = load_jobs()

st.subheader("📡 Pipeline Job Feed")

if df.empty:
    st.warning("No pipeline data found. Run: python indexer/pipeline.py")
    st.stop()

# =========================================================
# SCORING
# =========================================================

def score_row(row):

    return score_job(type("Job", (), {
        "title": row.get("title", ""),
        "company": row.get("company", "")
    }))


df["score"] = df.apply(score_row, axis=1)

df = df.sort_values("score", ascending=False)

# =========================================================
# METRICS
# =========================================================

st.subheader("📊 Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Jobs", len(df))
col2.metric("Top Score", int(df["score"].max()))
col3.metric("Avg Score", int(df["score"].mean()))

# =========================================================
# TOP JOBS
# =========================================================

st.subheader("🎯 Ranked Opportunities")

for _, row in df.head(50).iterrows():

    st.markdown(f"### {row['title']}")
    st.write(f"🏢 {row['company']} | {row.get('source','')}")
    st.write(f"🔗 {row.get('url','')}")
    st.write(f"🎯 Score: {row['score']} / 100")

    st.divider()

# =========================================================
# COMPANY BREAKDOWN
# =========================================================

st.subheader("🏢 Firm Activity")

if "company" in df.columns:

    firm_counts = df["company"].value_counts().head(15)

    st.bar_chart(firm_counts)
