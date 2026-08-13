from agents.job_finder import search_greenhouse_boards
from database import add_job


COMPANIES = [
    "stripe",
    "datadog",
    "cloudflare",
    "mongodb",
    "robinhood",
    "affirm",
    "figma",
    "coinbase",
]


jobs = search_greenhouse_boards(COMPANIES)


print()
print("=" * 60)
print(f"TOTAL RELEVANT INTERNSHIPS: {len(jobs)}")
print("=" * 60)


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

    relevance_score = job.get(
        "relevance_score",
        0
    )

    print()
    print(f"{title}")
    print(f"Company: {company}")
    print(f"Location: {location}")
    print(f"Score: {relevance_score}")
    print(url)

    add_job(
        company=company,
        title=title,
        location=location,
        url=url,
        description=description
    )


print()
print("Jobs saved to database.")