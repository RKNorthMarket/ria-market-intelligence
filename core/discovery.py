import json
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_PATH = os.path.join(BASE_DIR, "data", "profile.json")


def load_profile():
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def score_discovered_role(title, description, location="", salary_min=0):
    profile = load_profile()

    score = 0
    reasons = []

    text = f"{title} {description}".lower()
    location_text = str(location).lower()

    for target_title in profile["target_titles"]:
        if target_title.lower() in text:
            score += 20
            reasons.append(f"Title match: {target_title}")

    for industry in profile["target_industries"]:
        if industry.lower() in text:
            score += 15
            reasons.append(f"Industry match: {industry}")

    for keyword in profile["positive_keywords"]:
        if keyword.lower() in text:
            score += 5
            reasons.append(f"Keyword match: {keyword}")

    for keyword in profile["negative_keywords"]:
        if keyword.lower() in text:
            score -= 15
            reasons.append(f"Negative signal: {keyword}")

    for preferred_location in profile["preferred_locations"]:
        if preferred_location.lower() in location_text:
            score += 10
            reasons.append(f"Location match: {preferred_location}")

    try:
        salary_min = int(salary_min)
    except Exception:
        salary_min = 0

    if salary_min >= profile["target_base_salary"]:
        score += 15
        reasons.append("Salary meets target base threshold")
    elif salary_min >= profile["minimum_base_salary"]:
        score += 8
        reasons.append("Salary meets minimum base threshold")
    elif salary_min > 0:
        score -= 10
        reasons.append("Salary appears below minimum threshold")

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

    return {
        "fit_score": score,
        "priority": priority,
        "recommendation": recommendation,
        "reasons": reasons,
    }
