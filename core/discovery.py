import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(BASE_DIR, "data", "profile.json")
RESUME_PROFILE_PATH = os.path.join(BASE_DIR, "data", "resume_profile.json")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_profile():
    return load_json(PROFILE_PATH)


def load_resume_profile():
    return load_json(RESUME_PROFILE_PATH)


def _contains_any(text, terms):
    matches = []
    text_lower = text.lower()

    for term in terms:
        if term.lower() in text_lower:
            matches.append(term)

    return matches


def score_discovered_role(title, description, location="", salary_min=0):
    search_profile = load_profile()
    resume_profile = load_resume_profile()

    score = 0
    reasons = []
    strengths = []
    concerns = []

    combined_text = f"{title} {description}".lower()
    location_text = str(location).lower()

    # --------------------------------------------------
    # Search profile title alignment
    # --------------------------------------------------
    title_matches = _contains_any(
        combined_text,
        search_profile.get("target_titles", [])
    )

    if title_matches:
        score += min(25, len(title_matches) * 10)
        for match in title_matches[:3]:
            reasons.append(f"Target title alignment: {match}")

    # --------------------------------------------------
    # Industry alignment
    # --------------------------------------------------
    industry_matches = _contains_any(
        combined_text,
        search_profile.get("target_industries", [])
    )

    if industry_matches:
        score += min(25, len(industry_matches) * 8)
        for match in industry_matches[:4]:
            reasons.append(f"Industry alignment: {match}")

    # --------------------------------------------------
    # Positive keyword alignment
    # --------------------------------------------------
    keyword_matches = _contains_any(
        combined_text,
        search_profile.get("positive_keywords", [])
    )

    if keyword_matches:
        score += min(25, len(keyword_matches) * 3)
        for match in keyword_matches[:6]:
            reasons.append(f"Search keyword match: {match}")

    # --------------------------------------------------
    # Resume strength alignment
    # --------------------------------------------------
    resume_strength_matches = _contains_any(
        combined_text,
        resume_profile.get("core_strengths", [])
    )

    if resume_strength_matches:
        score += min(30, len(resume_strength_matches) * 5)
        for match in resume_strength_matches[:6]:
            strengths.append(f"Resume strength alignment: {match}")

    # --------------------------------------------------
    # Industry experience alignment from resume
    # --------------------------------------------------
    resume_industry_matches = _contains_any(
        combined_text,
        resume_profile.get("industries", [])
    )

    if resume_industry_matches:
        score += min(20, len(resume_industry_matches) * 5)
        for match in resume_industry_matches[:4]:
            strengths.append(f"Relevant industry background: {match}")

    # --------------------------------------------------
    # Leadership / executive scope
    # --------------------------------------------------
    leadership_terms = [
        "lead",
        "leader",
        "leadership",
        "executive",
        "manage",
        "manager",
        "director",
        "head",
        "vp",
        "vice president",
        "coo",
        "strategy",
        "transformation",
        "scale",
        "scaling"
    ]

    leadership_matches = _contains_any(combined_text, leadership_terms)

    if leadership_matches:
        score += min(20, len(leadership_matches) * 3)
        strengths.append(
            "Role appears to include leadership, transformation, or scaling scope."
        )

    # --------------------------------------------------
    # Accomplishment-based alignment
    # --------------------------------------------------
    accomplishment_signals = [
        "build",
        "built",
        "scale",
        "scaled",
        "improve",
        "improvement",
        "workflow",
        "technology",
        "crm",
        "service model",
        "advisor",
        "client experience",
        "operational efficiency",
        "transformation"
    ]

    accomplishment_matches = _contains_any(combined_text, accomplishment_signals)

    if accomplishment_matches:
        score += min(20, len(accomplishment_matches) * 3)
        strengths.append(
            "Role appears to align with prior accomplishments in scaling, workflow improvement, technology implementation, or service transformation."
        )

    # --------------------------------------------------
    # Location alignment
    # --------------------------------------------------
    location_matches = _contains_any(
        location_text,
        search_profile.get("preferred_locations", [])
    )

    if location_matches:
        score += 10
        reasons.append(f"Preferred location match: {location_matches[0]}")

    # --------------------------------------------------
    # Salary alignment
    # --------------------------------------------------
    try:
        salary_min = int(salary_min)
    except Exception:
        salary_min = 0

    minimum_base = int(search_profile.get("minimum_base_salary", 150000))
    target_base = int(search_profile.get("target_base_salary", 175000))

    if salary_min >= target_base:
        score += 15
        reasons.append("Salary meets or exceeds target base threshold.")
    elif salary_min >= minimum_base:
        score += 8
        reasons.append("Salary meets minimum base threshold.")
    elif salary_min > 0:
        score -= 10
        concerns.append("Salary appears below your stated minimum threshold.")

    # --------------------------------------------------
    # Negative signals
    # --------------------------------------------------
    negative_matches = _contains_any(
        combined_text,
        search_profile.get("negative_keywords", [])
    )

    if negative_matches:
        score -= min(40, len(negative_matches) * 15)
        for match in negative_matches[:5]:
            concerns.append(f"Negative role signal: {match}")

    # --------------------------------------------------
    # Advisor / producer caution
    # --------------------------------------------------
    producer_terms = [
        "book of business",
        "sales quota",
        "production",
        "producer",
        "financial advisor",
        "wealth advisor",
        "build your book"
    ]

    producer_matches = _contains_any(combined_text, producer_terms)

    if producer_matches:
        score -= 30
        concerns.append(
            "Role may be production-oriented rather than operations/client service leadership."
        )

    # --------------------------------------------------
    # Normalize
    # --------------------------------------------------
    score = max(0, min(score, 100))

    if score >= 90:
        priority = "High"
        recommendation = "Review"
    elif score >= 75:
        priority = "Medium"
        recommendation = "Review"
    else:
        priority = "Low"
        recommendation = "Deprioritize"

    # --------------------------------------------------
    # Executive summary
    # --------------------------------------------------
    if score >= 90:
        executive_summary = (
            "Strong executive fit based on alignment with your wealth management, "
            "operations leadership, client service, advisor enablement, and transformation background."
        )
    elif score >= 75:
        executive_summary = (
            "Potential fit. The role shows some alignment with your background, "
            "but should be reviewed for compensation, authority, and strategic scope."
        )
    else:
        executive_summary = (
            "Lower-priority fit based on the current profile and role description. "
            "Review only if there is a strategic reason not captured in the posting."
        )

    return {
        "fit_score": score,
        "priority": priority,
        "recommendation": recommendation,
        "reasons": reasons,
        "strengths": strengths,
        "concerns": concerns,
        "executive_summary": executive_summary,
    }
