from agents.job_finder import search_all_jobs
from database import add_job


GREENHOUSE_COMPANIES = [
    "stripe",
    "datadog",
    "cloudflare",
    "mongodb",
    "robinhood",
    "affirm",
    "figma",
    "coinbase",
]


LEVER_COMPANIES = [
    "palantir",
    "anduril",
    "scaleai",
    "ramp",
    "verkada",
    "samsara",
]


jobs = search_all_jobs(
    GREENHOUSE_COMPANIES,
    LEVER_COMPANIES
)


saved = 0


for job in jobs:
    title = job.get(
        "title",
        "Unknown title"
    )

    company = job.get(
        "source_company",
        "Unknown company"
    )

    location = job.get(
        "location",
        {}
    ).get(
        "name",
        "Unknown location"
    )

    url = job.get(
        "absolute_url",
        ""
    )

    description = job.get(
        "content",
        ""
    )

    add_job(
        company=company,
        title=title,
        location=location,
        url=url,
        description=description
    )

    saved += 1


print()
print("=" * 60)
print(f"FOUND: {len(jobs)}")
print(f"PROCESSED FOR DATABASE: {saved}")
print("=" * 60)
print()
print("Job refresh complete.")
