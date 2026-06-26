from core.models import Job


def score_job(job: Job) -> int:
    """
    Placeholder.
    Will become the executive opportunity engine.
    """

    score = 0

    title = job.title.lower()

    if "director" in title:
        score += 25

    if "vice president" in title or "vp" in title:
        score += 30

    if "head" in title:
        score += 30

    if "operations" in title:
        score += 20

    if "wealth" in title:
        score += 15

    return min(score, 100)
