import streamlit as st
from core.discovery import score_discovered_role

st.set_page_config(page_title="Analyze Role", layout="wide")

st.title("🧠 Analyze New Role")
st.caption("Score a potential opportunity against your executive search profile.")

st.markdown("## Role Intake")

title = st.text_input("Job Title")
company = st.text_input("Company")
location = st.text_input("Location")
job_url = st.text_input("Job Posting URL")
salary_min = st.number_input("Minimum Base Salary", min_value=0, step=5000)

description = st.text_area(
    "Job Description",
    height=350,
    placeholder="Paste the full job description here..."
)

analyze = st.button("Analyze Role")

if analyze:
    if not title or not description:
        st.warning("Please enter at least a job title and job description.")
        st.stop()

    result = score_discovered_role(
        title=title,
        description=description,
        location=location,
        salary_min=salary_min
    )

    fit_score = result["fit_score"]
    priority = result["priority"]
    recommendation = result["recommendation"]
    reasons = result["reasons"]

    st.divider()

    st.header("Executive Fit Review")

    c1, c2, c3 = st.columns(3)

    c1.metric("Fit Score", fit_score)
    c2.metric("Priority", priority)
    c3.metric("Recommendation", recommendation)

    st.divider()

    st.subheader("Executive Recommendation")

    if fit_score >= 90:
        st.success(
            "This appears to be a strong executive-search fit. Review closely and consider moving it into your active pipeline."
        )
    elif fit_score >= 75:
        st.info(
            "This may be worth reviewing further, but it should not automatically outrank stronger opportunities."
        )
    else:
        st.warning(
            "This does not appear to be a priority match based on your current search profile."
        )

    st.subheader("Why This Role Matches")

    if reasons:
        for reason in reasons:
            st.write(f"- {reason}")
    else:
        st.write("No strong matching signals were found.")

    st.divider()

    st.subheader("Executive Coach Notes")

    if fit_score >= 90:
        st.write(
            """
Recommended next steps:

- Confirm compensation range.
- Confirm reporting structure.
- Determine whether the role is strategic, execution-heavy, or both.
- Identify whether the position owns operations, client service, advisor experience, or platform leadership.
- If interested, add it to Discovery Inbox or Active Pipeline.
"""
        )
    elif fit_score >= 75:
        st.write(
            """
Recommended next steps:

- Review the company more closely.
- Check whether this is a true leadership role or an individual contributor role.
- Confirm whether compensation and location justify the time investment.
"""
        )
    else:
        st.write(
            """
Recommended next steps:

- Do not prioritize unless there is a strategic reason.
- Watch for CFP, sales quota, branch manager, or advisor-production signals.
"""
        )

    st.divider()

    st.subheader("Manual Next Action")

    st.info(
        "For now, copy this role into discovery.csv if you want to keep it in your Discovery Inbox. In a later step, we will add a one-click Save to Discovery feature."
    )

    st.markdown("### Suggested CSV Row")

    csv_row = f'''NEXT_ID,{title},{company},"{location}",Full-Time,{salary_min},0,,{job_url},Manual,{fit_score},{priority},{recommendation},New,"Analyzed manually in ECIP."'''

    st.code(csv_row, language="csv")
