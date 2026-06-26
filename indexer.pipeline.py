import os
import pandas as pd
from datetime import datetime

from indexer.greenhouse import get_greenhouse_jobs


DATA_PATH = "data/jobs.csv"


# =========================================================
# NORMALIZATION HELPERS
# =========================================================

def job_to_dict(job):
    return {
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.url,
        "source": job.source,
        "ats": job.ats,
        "date_posted": str(job.date_posted),
        "ingested_at": datetime.utcnow().isoformat()
    }


def deduplicate(jobs):
    """
    Remove duplicate jobs using (title + company + location)
    """

    seen = set()
    unique = []

    for j in jobs:
        key = (j.title.lower(), j.company.lower(), j.location.lower())

        if key in seen:
            continue

        seen.add(key)
        unique.append(j)

    return unique


# =========================================================
# PIPELINE CORE
# =========================================================

def run_pipeline():

    print("📡 Running RIA job pipeline...")

    # -----------------------------
    # STEP 1: INGEST GREENHOUSE
    # -----------------------------
    jobs = get_greenhouse_jobs()

    print(f"✔ Greenhouse jobs pulled: {len(jobs)}")

    # -----------------------------
    # STEP 2: DEDUPLICATE
    # -----------------------------
    jobs = deduplicate(jobs)

    print(f"✔ After deduplication: {len(jobs)}")

    # -----------------------------
    # STEP 3: CONVERT TO DICT
    # -----------------------------
    records = [job_to_dict(j) for j in jobs]

    # -----------------------------
    # STEP 4: WRITE CSV
    # -----------------------------
    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame(records)

    df.to_csv(DATA_PATH, index=False)

    print(f"✔ Saved {len(df)} jobs to {DATA_PATH}")

    return df


# =========================================================
# LOCAL TEST RUN
# =========================================================

if __name__ == "__main__":
    run_pipeline()
