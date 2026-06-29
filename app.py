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

# ---------- Executive Dashboard ----------

active_jobs = filtered[
    ~filtered["status"].isin(["Closed"])
]

active_count = len(active_jobs)

applied_count = len(
    active_jobs[
        active_jobs["status"] == "Applied"
    ]
)

interview_count = len(
    active_jobs[
        active_jobs["status"].str.contains(
            "Interview",
            case=False,
            na=False
        )
    ]
)

referral_count = len(
    active_jobs[
        active_jobs["status"] == "Referred"
    ]
)

avg_fit = (
    round(active_jobs["fit_score"].mean(), 1)
    if active_count > 0 else 0
)

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric(
    "Active Opportunities",
    active_count
)

c2.metric(
    "Applied",
    applied_count
)

c3.metric(
    "Interviewing",
    interview_count
)

c4.metric(
    "Referrals",
    referral_count
)

c5.metric(
    "Avg Fit",
    avg_fit
)

st.divider()

st.subheader("Executive Opportunity Pipeline")

display_columns = [
    "company",
    "title",
    "status",
    "priority",
    "fit_score",
    "next_step",
    "last_activity"
]

display_df = (
    filtered[display_columns]
    .sort_values(
        by=["fit_score", "company"],
        ascending=[False, True]
    )
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

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
