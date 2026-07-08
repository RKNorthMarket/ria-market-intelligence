import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(BASE_DIR, "data", "profile.json")
RESUME_PROFILE_PATH = os.path.join(BASE_DIR, "data", "resume_profile.json")

DISCOVERY_ENGINE_VERSION = "v3_resume_signal_engine"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_profile():
    return load_json(PROFILE_PATH)


def load_resume_profile():
    return load_json(RESUME_PROFILE_PATH)


def contains_terms(text, terms):
    text = text.lower()
    return [term for term in terms if term.lower() in text]


def score_discovered_role(title, description, location="", salary_min=0):
    search_profile = load_profile()
    resume_profile = load_resume_profile()

    text = f"{title} {description}".lower()
    location_text = str(location).lower()

    score = 0
    reasons = []
    strengths = []
    concerns = []

    signal_groups = {
        "Executive / Leadership Scope": [
            "director", "head", "vice president", "vp", "coo", "chief",
            "executive", "lead", "leader", "leadership", "manage",
            "manager", "oversight", "strategy", "strategic"
        ],
        "Operations Leadership": [
            "operations", "operational", "process", "workflow",
            "service model", "efficiency", "execution", "transformation",
            "scaling", "scale", "operating model"
        ],
        "Client Service / Client Experience": [
            "client service", "client experience", "client success",
            "client solutions", "service delivery", "relationship management",
            "client operations"
        ],
        "Advisor / RIA / Wealth Management": [
            "wealth", "wealth management", "ria", "registered investment advisor",
            "advisor", "adviser", "private wealth", "family office",
            "asset management", "custody", "custodian", "broker dealer",
            "trust company"
        ],
        "Platform / Technology / Enablement": [
            "platform", "crm", "salesforce", "hubspot", "technology",
            "automation", "reporting", "dashboard", "data",
            "advisor enablement", "practice management"
        ],
        "Build / Improve / Transform": [
            "build", "built", "develop", "launch", "create", "improve",
            "modernize", "redesign", "optimize", "transform",
            "change management"
        ]
    }

    weights = {
        "Executive / Leadership Scope": 18,
        "Operations Leadership": 20,
        "Client Service / Client Experience": 18,
        "Advisor / RIA / Wealth Management": 22,
        "Platform / Technology / Enablement": 12,
        "Build / Improve / Transform": 10
    }

    for group, terms in signal_groups.items():
        matches = contains_terms(text, terms)
        if matches:
            score += weights[group]
            strengths.append(f"{group}: {', '.join(matches[:5])}")

    title_matches = contains_terms(text, search_profile.get("target_titles", []))
    if title_matches:
        score += 15
        reasons.append(f"Target title match: {', '.join(title_matches[:3])}")

    positive_matches = contains_terms(text, search_profile.get("positive_keywords", []))
    if positive_matches:
        score += min(15, len(positive_matches) * 3)
        reasons.append(f"Positive search signals: {', '.join(positive_matches[:6])}")

    resume_matches = contains_terms(text, resume_profile.get("core_strengths", []))
    if resume_matches:
        score += min(15, len(resume_matches) * 4)
        strengths.append(f"Resume strength alignment: {', '.join(resume_matches[:5])}")

    location_matches = contains_terms(
        location_text,
        search_profile.get("preferred_locations", [])
    )
    if location_matches:
        score += 8
        reasons.append(f"Preferred location match: {location_matches[0]}")

    try:
        salary_min = int(salary_min)
    except Exception:
        salary_min = 0

    minimum_base = int(search_profile.get("minimum_base_salary", 150000))
    target_base = int(search_profile.get("target_base_salary", 175000))

    if salary_min >= target_base:
        score += 12
        reasons.append("Salary meets or exceeds target base threshold.")
    elif salary_min >= minimum_base:
        score += 7
        reasons.append("Salary meets minimum base threshold.")
    elif salary_min > 0:
        score -= 10
        concerns.append("Salary appears below your minimum threshold.")

    negative_matches = contains_terms(text, search_profile.get("negative_keywords", []))
    if negative_matches:
        score -= min(35, len(negative_matches) * 12)
        concerns.append(f"Negative signals: {', '.join(negative_matches[:5])}")

    producer_terms = [
        "book of business", "sales quota", "producer",
        "financial advisor", "wealth advisor", "build your book"
    ]

    producer_matches = contains_terms(text, producer_terms)
    if producer_matches:
        score -= 30
        concerns.append("Role may be production/sales-oriented rather than operations leadership.")

    score = max(0, min(score, 100))

    if score >= 90:
        priority = "High"
        recommendation = "Review"
        executive_summary = "Strong executive fit based on leadership, operations, wealth management, client service, and transformation alignment."
    elif score >= 75:
        priority = "Medium"
        recommendation = "Review"
        executive_summary = "Potential fit. Review for compensation, authority, leadership scope, and company quality."
    else:
        priority = "Low"
        recommendation = "Deprioritize"
        executive_summary = "Lower-priority fit based on the current role description and search profile."

    return {
        "engine_version": DISCOVERY_ENGINE_VERSION,
        "fit_score": score,
        "priority": priority,
        "recommendation": recommendation,
        "reasons": reasons,
        "strengths": strengths,
        "concerns": concerns,
        "executive_summary": executive_summary
    }
