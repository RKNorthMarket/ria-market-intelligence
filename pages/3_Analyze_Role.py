import streamlit as st
from core.discovery import score_discovered_role

st.set_page_config(page_title="Analyze Role", layout="wide")

st.title("🧠 Analyze New Role")
st.caption("Paste a job description and score it against your Discovery Profile.")

title = st.text_input("Job Title")
company = st.text_input("Company")
location = st.text_input("Location")
salary_min = st.number_input("Minimum Base Salary", min_value=0, step=5000)

description = st.text_area(
    "Job Description",
    height=300,
    placeholder="Paste the full job description here..."
)

if st.button("Analyze Role"):
    if not title or not description:
        st.warning("Please enter at least a job title and job description.")
    else:
        result = score_discovered_role(
            title=title,
            description=description,
            location=location,
            salary_min=salary_min
        )

        st.subheader("Fit Analysis")

        st.metric("Fit Score", result["fit_score"])
        st.metric("Priority", result["priority"])
        st.metric("Recommendation", result["recommendation"])

        st.subheader("Why")
        if result["reasons"]:
            for reason in result["reasons"]:
                st.write(f"- {reason}")
        else:
            st.write("No strong matching signals found.")

        if result["fit_score"] >= 90:
            st.success("This looks like a strong executive-search fit.")
        elif result["fit_score"] >= 75:
            st.info("This may be worth reviewing further.")
        else:
            st.warning("This does not appear to be a priority match.")
