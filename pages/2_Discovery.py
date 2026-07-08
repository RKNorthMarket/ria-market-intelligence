import streamlit as st
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DISCOVERY_PATH = os.path.join(BASE_DIR, "data", "discovery.csv")

st.set_page_config(page_title="Opportunity Discovery", layout="wide")

st.title("🔎 Opportunity Discovery")
st.caption("Review potential new roles before promoting them into your active pipeline.")

if not os.path.exists(DISCOVERY_PATH):
    st.error(f"Missing discovery file: {DISCOVERY_PATH}")
    st.stop()

df = pd.read_csv(DISCOVERY_PATH).fillna("")

for c in ["salary_min", "salary_max", "fit_score"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

st.sidebar.header("Discovery Filters")

status_options = ["All"] + sorted([s for s in df["status"].unique() if s != ""])
priority_options = ["All"] + sorted([p for p in df["priority"].unique() if p != ""])
recommendation_options = ["All"] + sorted([r for r in df["recommendation"].unique() if r != ""])

status = st.sidebar.selectbox("Status", status_options)
priority = st.sidebar.selectbox("Priority", priority_options)
recommendation = st.sidebar.selectbox("Recommendation", recommendation_options)
min_fit = st.sidebar.slider("Minimum Fit Score", 0, 100, 70)
search = st.sidebar.text_input("Search")

filtered = df.copy()

if status != "All":
    filtered = filtered[filtered["status"] == status]

if priority != "All":
    filtered = filtered[filtered["priority"] == priority]

if recommendation != "All":
    filtered = filtered[filtered["recommendation"] == recommendation]

filtered = filtered[filtered["fit_score"] >= min_fit]

if search:
    s = search.lower()
    filtered = filtered[
        filtered["title"].str.lower().str.contains(s, na=False)
        | filtered["company"].str.lower().str.contains(s, na=False)
    ]

new_count = len(filtered[filtered["status"] == "New"])
review_count = len(filtered[filtered["recommendation"] == "Review"])
high_count = len(filtered[filtered["priority"] == "High"])
avg_fit = round(filtered["fit_score"].mean(), 1) if len(filtered) else 0

c1, c2, c3, c4 = st.columns(4)

c1.metric("New Opportunities", new_count)
c2.metric("Recommended Review", review_count)
c3.metric("High Priority", high_count)
c4.metric("Avg Fit", avg_fit)

st.divider()

st.subheader("Opportunity Inbox")

if len(filtered) == 0:
    st.info("No discovery opportunities match the current filters.")
    st.stop()

display_columns = [
    "company",
    "title",
    "location",
    "priority",
    "fit_score",
    "recommendation",
    "status",
    "source",
]

display_df = filtered[display_columns].sort_values(
    by=["fit_score", "company"],
    ascending=[False, True],
)

st.dataframe(display_df, use_container_width=True, hide_index=True)

st.divider()

st.subheader("Discovery Detail")

idx = st.selectbox(
    "Select a discovered opportunity",
    filtered.index,
    format_func=lambda i: f"{filtered.loc[i, 'company']} — {filtered.loc[i, 'title']}",
)

role = filtered.loc[idx]

left, right = st.columns([2, 1])

with left:
    st.markdown(f"## {role['title']}")
    st.write(f"**Company:** {role['company']}")
    st.write(f"**Location:** {role['location']}")
    st.write(f"**Employment Type:** {role['employment_type']}")
    st.write(f"**Source:** {role['source']}")
    st.write(f"**Posting Date:** {role['posting_date']}")
    st.write(f"**Status:** {role['status']}")
    st.write(f"**Recommendation:** {role['recommendation']}")
    st.write(f"**Notes:** {role['notes']}")

    if str(role["job_url"]).strip():
        st.markdown(f"[🔗 Open Job Posting]({role['job_url']})")
    else:
        st.info("No job posting URL has been saved for this discovered opportunity.")

with right:
    st.metric("Fit Score", int(role["fit_score"]))

    if role["salary_max"] > 0:
        st.metric(
            "Salary Range",
            f"${int(role['salary_min']):,} - ${int(role['salary_max']):,}",
        )
    else:
        st.metric("Salary Range", "N/A")

st.divider()

st.subheader("Decision Guidance")

fit = int(role["fit_score"])

if fit >= 90 and role["recommendation"] == "Review":
    st.success("High-fit discovered opportunity. Review closely and consider promoting to your active pipeline.")
elif fit >= 80:
    st.info("Potentially relevant opportunity. Review selectively.")
else:
    st.warning("Lower-fit opportunity. Consider dismissing unless there is a strategic reason to pursue.")

st.markdown("### Suggested Actions")
st.write("- Promote to active pipeline if this is worth pursuing.")
st.write("- Archive if interesting but not timely.")
st.write("- Dismiss if it does not meet your executive search criteria.")

st.caption("Discovery Inbox • Version 1.0")
