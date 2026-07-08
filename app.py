import streamlit as st
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "jobs.csv")

st.set_page_config(page_title="RIA Executive OS", layout="wide")

st.title("🧠 RIA Executive OS")
st.caption("Executive Career Intelligence Dashboard")

if not os.path.exists(DATA_PATH):
    st.error(f"Missing data file: {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH).fillna("")

for c in ["salary_min", "salary_max", "fit_score"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

st.sidebar.header("Filters")

status_options = ["All"] + sorted([s for s in df["status"].unique() if s != ""])
priority_options = ["All"] + sorted([p for p in df["priority"].unique() if p != ""])
company_options = ["All"] + sorted([c for c in df["company"].unique() if c != ""])

status = st.sidebar.selectbox("Status", status_options)
priority = st.sidebar.selectbox("Priority", priority_options)
company = st.sidebar.selectbox("Company", company_options)
min_fit = st.sidebar.slider("Minimum Fit Score", 0, 100, 70)
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
        filtered["title"].str.lower().str.contains(s, na=False)
        | filtered["company"].str.lower().str.contains(s, na=False)
    ]

active_jobs = filtered[filtered["status"] != "Closed"]

active_count = len(active_jobs)
applied_count = len(active_jobs[active_jobs["status"] == "Applied"])
interview_count = len(
    active_jobs[
        active_jobs["status"].str.contains("Interview", case=False, na=False)
    ]
)
referral_count = len(active_jobs[active_jobs["status"] == "Referred"])
avg_fit = round(active_jobs["fit_score"].mean(), 1) if active_count > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Active Opportunities", active_count)
c2.metric("Applied", applied_count)
c3.metric("Interviewing", interview_count)
c4.metric("Referrals", referral_count)
c5.metric("Avg Fit", avg_fit)

st.divider()

st.subheader("Executive Opportunity Pipeline")

if len(filtered) == 0:
    st.info("No opportunities match the current filters.")
    st.stop()

display_columns = [
    "company",
    "title",
    "status",
    "priority",
    "fit_score",
    "next_step",
    "last_activity",
]

display_df = (
    filtered[display_columns]
    .sort_values(by=["fit_score", "company"], ascending=[False, True])
)

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Opportunity Details")

idx = st.selectbox(
    "Select an Opportunity",
    filtered.index,
    format_func=lambda i: f"{filtered.loc[i, 'company']} — {filtered.loc[i, 'title']}",
)

job = filtered.loc[idx]

left, right = st.columns([2, 1])

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
        st.markdown(f"[🔗 Open Job Posting]({job['job_url']})")
    else:
        st.info("No job posting URL has been saved for this opportunity.")

with right:
    st.metric("Fit Score", int(job["fit_score"]))

    if job["salary_max"] > 0:
        st.metric(
            "Salary Range",
            f"${int(job['salary_min']):,} - ${int(job['salary_max']):,}",
        )
    else:
        st.metric("Salary Range", "N/A")

st.divider()

st.header("🧠 Executive Opportunity Workspace")

st.subheader("Executive Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Company", job["company"])
c2.metric("Status", job["status"])
c3.metric("Priority", job["priority"])
c4.metric("Fit Score", int(job["fit_score"]))

st.write(f"**Location:** {job['location']}")
st.write(f"**Employment Type:** {job['employment_type']}")

if job["salary_max"] > 0:
    st.write(
        f"**Salary Range:** ${int(job['salary_min']):,} - ${int(job['salary_max']):,}"
    )
else:
    st.write("**Salary Range:** N/A")

st.markdown(f"**Next Step:** {job['next_step']}")
st.markdown(f"**Last Activity:** {job['last_activity']}")

st.divider()

st.subheader("🧭 Strategic Assessment")

fit = int(job["fit_score"])

if fit >= 95:
    st.success("Exceptional strategic fit — prioritize aggressively.")
elif fit >= 90:
    st.info("Strong fit — high priority opportunity.")
elif fit >= 85:
    st.warning("Moderate fit — pursue selectively.")
else:
    st.error("Lower fit — consider deprioritizing.")

st.divider()

st.subheader("🚀 Executive Action Center")

action_col1, action_col2 = st.columns(2)

with action_col1:
    st.markdown("### Immediate Next Action")
    st.info(job["next_step"])

    st.markdown("### Last Activity")
    st.write(job["last_activity"])

with action_col2:
    st.markdown("### Opportunity Summary")
    st.write(f"**Company:** {job['company']}")
    st.write(f"**Role:** {job['title']}")
    st.write(f"**Current Status:** {job['status']}")
    st.write(f"**Priority:** {job['priority']}")

st.divider()

st.subheader("🎯 Executive Coaching")

if fit >= 95:
    st.success(
        """
This appears to be one of your strongest opportunities.

Recommended focus:

- Continue aggressive pursuit
- Prepare deeply for interviews
- Research executive leadership team
- Build a 30/60/90-day strategy
"""
    )
elif fit >= 90:
    st.info(
        """
Very strong opportunity.

Recommended focus:

- Maintain recruiter communication
- Continue networking
- Prepare company-specific examples
"""
    )
else:
    st.warning(
        """
Good opportunity, but not top tier.

Continue pursuing while prioritizing stronger matches.
"""
    )

st.divider()

st.subheader("🏢 Company Research Checklist")

st.checkbox("Understand company business model")
st.checkbox("Research executive leadership")
st.checkbox("Review recent news")
st.checkbox("Review Glassdoor feedback")
st.checkbox("Understand competitive landscape")
st.checkbox("Prepare questions for interviewer")
st.checkbox("Develop 30/60/90 Day Plan")
st.checkbox("Review compensation expectations")

st.divider()

tab1, tab2, tab3 = st.tabs(
    ["🎯 Interview Preparation", "📅 Follow-Up Planner", "📁 Documents"]
)

with tab1:
    st.subheader("Interview Preparation")

    st.text_area(
        "Key talking points",
        placeholder="e.g. RIA operations leadership, advisor enablement, scaling service models...",
    )

    st.text_area(
        "Questions to ask",
        placeholder="e.g. How is success measured in the first 90 days?",
    )

    st.text_area(
        "Interview notes",
        placeholder="Capture insights from recruiter / hiring manager conversations",
    )

with tab2:
    st.subheader("Follow-Up Planner")

    st.date_input("Next follow-up date")
    st.text_area("Follow-up message / action")
    st.checkbox("Mark follow-up completed")

with tab3:
    st.subheader("Documents")

    st.text_input("Resume version used")
    st.text_area("Cover letter notes")
    st.text_area("Thank-you email draft")
    st.text_area("Additional notes")

st.caption("RIA Executive OS • Version 2.0")
