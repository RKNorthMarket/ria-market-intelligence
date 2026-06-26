import requests
from datetime import datetime

from core.models import Job
from core.settings import REQUEST_TIMEOUT


GREENHOUSE_BOARDS = [
    "hightoweradvisors",
    "focusfinancialpartners",
    "commonwealthfinancialnetwork",
    "marinerwealthadvisors"
]


def fetch_board(board: str):
    """
    Pull raw Greenhouse job JSON
    """
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs"

    try:
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        if r.status_code != 200:
            return []

        data = r.json()
        return data.get("jobs", [])

    except Exception:
        return []


def normalize_job(board: str, raw: dict) -> Job:
    """
    Convert Greenhouse job → canonical Job model
    """

    return Job(
        title=raw.get("title", ""),
        company=board,
        location=raw.get("location", {}).get("name", ""),
        description="",
        url=raw.get("absolute_url", ""),
        source="greenhouse",
        ats="greenhouse",
        date_posted=None
    )


def get_greenhouse_jobs():
    """
    Main entrypoint used by pipeline
    """

    jobs = []

    for board in GREENHOUSE_BOARDS:
        raw_jobs = fetch_board(board)

        for j in raw_jobs:
            try:
                job = normalize_job(board, j)
                jobs.append(job)
            except Exception:
                continue

    return jobs
