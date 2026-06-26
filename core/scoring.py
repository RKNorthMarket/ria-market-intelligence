def score_job(job):
    """
    Simple heuristic scoring model for job ranking.
    Replace later with RIA OS-weighted model.
    """

    score = 0

    title = str(job.get("title", "")).lower()
    description = str(job.get("description", "")).lower()
    company = str(job.get("company", "")).lower()

    # -------------------------
    # TITLE SIGNALS
    # -------------------------
    executive_keywords = ["vp", "vice president", "director", "head", "chief", "managing"]
    ops_keywords = ["operations", "client service", "wealth", "ria", "advisor"]

    if any(k in title for k in executive_keywords):
        score += 30

    if any(k in title for k in ops_keywords):
        score += 25

    # -------------------------
    # DOMAIN MATCH (RIA/Wealth)
    # -------------------------
    ria_keywords = ["ria", "wealth", "advisor", "custody", "clearing", "asset"]
    if any(k in description for k in ria_keywords):
        score += 20

    # -------------------------
    # COMPANY QUALITY (light heuristic)
    # -------------------------
    tier1 = ["jpmorgan", "goldman", "fidelity", "schwab", "state street", "blackrock"]
    if any(c in company for c in tier1):
        score += 15

    # -------------------------
    # DEFAULT BASE SCORE
    # -------------------------
    score += 10

    return min(score, 100)
