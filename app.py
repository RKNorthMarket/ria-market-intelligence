import streamlit as st
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "jobs.csv")

st.set_page_config(page_title="RIA Executive OS", layout="wide")

st.title("🧠 RIA Executive OS")
st.caption("Executive Job Intelligence Dashboard")

if not os.path.exists(DATA_PATH):
    st.error(f"Missing data file: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)

# Fill missing values
df = df.fillna("")

# Ensure numeric columns
for c in ["salary_min","salary_max","fit_score"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

# ---------- Sidebar ----------
st.sidebar.header("Filters")

status_options = ["All"] + sorted([s for s in df["status"].unique() if s != ""])
status = st.sidebar.selectbox("Status", status_options)

priority_options = ["All"] + sorted([p for p in df["priority"].unique() if p != ""])
priority = st.sidebar.selectbox("Priority", priority_options)

company_options = ["All"] + sorted(df["company"].unique())
company = st.sidebar.selectbox("Company", company_options)

min_fit = st.sidebar.slider("Minimum Fit Score",0,100,70)

search = st.sidebar.text_input("Search")

filtered = df.copy()

if status != "All":
    filtered = filtered[filtered["status"] == status]

if priority != "All":
    filtered = filtered[filtered["priority"] == priority]

if company != "All":
    filtered = filtered[filtered["company"] == company]

filtered = filtered[filtered["fit_score"] >= min_fit]

if search:
    s = search.lower()
    filtered = filtered[
        filtered["title"].str.lower().str.contains(s) |
        filtered["company"].str.lower().str.contains(s)
    ]

# ---------- Metrics ----------
active = len(filtered[~filtered["status"].isin(["Rejected","Closed"])])
interviewing = len(filtered[filtered["status"].str.contains("Interview", case=False)])
applied = len(filtered[filtered["status"]=="Applied"])
avg_fit = round(filtered["fit_score"].mean(),1) if len(filtered) else 0

c1,c2,c3,c4 = st.columns(4)
c1.metric("Visible Opportunities",len(filtered))
c2.metric("Interviewing",interviewing)
c3.metric("Applied",applied)
c4.metric("Avg Fit",avg_fit)

st.divider()

st.subheader("Executive Opportunity Pipeline")

cols=["title","company","location","status","priority","fit_score"]
st.dataframe(filtered[cols].sort_values("fit_score",ascending=False),use_container_width=True)

st.divider()

st.subheader("Opportunity Details")

if len(filtered)==0:
    st.info("No opportunities match the current filters.")
    st.stop()

idx = st.selectbox(
    "Select an Opportunity",
    filtered.index,
    format_func=lambda i: f'{filtered.loc[i,"company"]} — {filtered.loc[i,"title"]}'
)

job = filtered.loc[idx]

left,right = st.columns([2,1])

with left:
    st.markdown(f"## {job['title']}")
    st.write(f"**Company:** {job['company']}")
    st.write(f"**Location:** {job['location']}")
    st.write(f"**Employment:** {job['employment_type']}")
    st.write(f"**Status:** {job['status']}")
    st.write(f"**Priority:** {job['priority']}")
    st.write(f"**Source:** {job['source']}")
    st.write(f"**Recruiter:** {job['recruiter']}")
    st.write(f"**Contact:** {job['contact']}")
    st.write(f"**Last Activity:** {job['last_activity']}")
    st.write(f"**Next Step:** {job['next_step']}")
    st.write(f"**Notes:** {job['notes']}")
    if str(job["job_url"]).strip():
        st.markdown(f"[Open Job Posting]({job['job_url']})")

with right:
    st.metric("Fit Score", int(job["fit_score"]))
    if job["salary_max"]>0:
        st.metric("Salary Range",
                  f"${int(job['salary_min']):,} - ${int(job['salary_max']):,}")
    else:
        st.metric("Salary Range","N/A")

st.divider()
st.caption("RIA Executive OS • Version 1.0")
