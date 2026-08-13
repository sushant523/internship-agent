from agents.job_finder import search_all_jobs


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


print()
print("=" * 60)
print(
    f"TOTAL MATCHING INTERNSHIPS: "
    f"{len(jobs)}"
)
print("=" * 60)


for job in jobs:

    print()

    print(
        f"[{job.get('source', '').upper()}]"
    )

    print(
        job.get(
            "title",
            "Unknown"
        )
    )

    print(
        job.get(
            "location",
            {}
        ).get(
            "name",
            "Unknown"
        )
    )

    print(
        f"Relevance: "
        f"{job.get('relevance_score', 0)}"
    )

    print(
        job.get(
            "absolute_url",
            ""
        )
    )