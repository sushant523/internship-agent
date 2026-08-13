import re
import html
import requests


# ============================================================
# YOUR TARGET CAREER AREAS
# ============================================================

HIGH_VALUE_TITLE_KEYWORDS = [
    "software engineer",
    "software developer",
    "software engineering",
    "backend",
    "frontend",
    "full stack",
    "full-stack",
    "developer",

    "cybersecurity",
    "cyber security",
    "information security",
    "security engineer",
    "security analyst",
    "application security",
    "cloud security",
    "network security",
    "security operations",
    "soc analyst",
    "vulnerability",
    "threat",

    "information technology",
    "it intern",
    "systems engineer",
    "systems administrator",
    "network engineer",
    "networking",
    "network strategy",
    "infrastructure",
    "cloud engineer",
    "cloud infrastructure",
    "devops",
    "site reliability",
    "sre",

    "data engineer",
    "data analyst",
    "data science",
    "machine learning",
    "artificial intelligence",
    "ai engineer",
    "research engineer",

    "computer science",
    "technology intern",
    "technical intern",
]


RESUME_SKILLS = [
    "python",
    "c++",
    "javascript",
    "sql",
    "rest api",
    "restful api",
    "git",
    "data structures",
    "object oriented programming",
    "oop",
    "relational database",
    "database",
    "llm",
    "rag",
    "logistic regression",
    "machine learning",
    "probability modeling",
    "data analysis",
    "data handling",
    "backend",
    "web application",
]


EXCLUDED_TITLE_KEYWORDS = [
    "accounting",
    "finance",
    "marketing",
    "sales",
    "human resources",
    "recruiting",
    "recruiter",
    "legal",
    "communications",
    "business development",
    "market research",
    "customer success",
    "public relations",
    "graphic design",
]


# ============================================================
# SHARED FILTERING
# ============================================================

def is_internship_title(title):
    return bool(
        re.search(
            r"\bintern(ship)?s?\b",
            title.lower()
        )
    )


def calculate_relevance(title, content):
    title_lower = title.lower()
    content_lower = content.lower()

    if any(
        keyword in title_lower
        for keyword in EXCLUDED_TITLE_KEYWORDS
    ):
        return 0

    score = 0

    for keyword in HIGH_VALUE_TITLE_KEYWORDS:
        if keyword in title_lower:
            score += 10

    for skill in RESUME_SKILLS:
        if skill in content_lower:
            score += 2

    return score


def is_relevant_job(title, content):
    return calculate_relevance(
        title,
        content
    ) >= 8


def is_us_location(location, content):
    location_lower = (location or "").lower().strip()
    content_lower = (content or "").lower()

    foreign_terms = [
        "france",
        "paris",
        "poland",
        "warsaw",
        "india",
        "bengaluru",
        "bangalore",
        "singapore",
        "london",
        "united kingdom",
        "uk",
        "germany",
        "berlin",
        "canada",
        "toronto",
    ]

    # If the actual location clearly says another country,
    # reject it immediately.
    if any(
        term in location_lower
        for term in foreign_terms
    ):
        return False

    us_phrases = [
        "united states",
        "new york",
        "new york city",
        "nyc",
        "brooklyn",
        "san francisco",
        "palo alto",
        "los angeles",
        "seattle",
        "austin",
        "boston",
        "chicago",
        "denver",
        "atlanta",
        "washington dc",
        "washington, dc",
        "remote us",
        "remote - us",
        "remote, us",
        "remote usa",
        "remote united states",
    ]

    # Trust the stated location first.
    if any(
        phrase in location_lower
        for phrase in us_phrases
    ):
        return True

    state_codes = [
        "NY", "NJ", "CA", "TX",
        "WA", "MA", "IL", "CO",
        "GA", "PA", "VA", "MD",
        "NC", "FL", "CT",
    ]

    for code in state_codes:
        if re.search(
            rf"\b{code.lower()}\b",
            location_lower
        ):
            return True

    # Some Greenhouse postings only say "In-Office".
    # In that case, inspect the description.
    vague_locations = [
        "",
        "in-office",
        "hybrid",
        "remote",
    ]

    if location_lower in vague_locations:

        if any(
            phrase in content_lower
            for phrase in us_phrases
        ):
            return True

        for code in state_codes:
            if re.search(
                rf"\b{code.lower()}\b",
                content_lower
            ):
                return True

    return False


# ============================================================
# GREENHOUSE
# ============================================================

def fetch_greenhouse_jobs(board_token):
    url = (
        f"https://boards-api.greenhouse.io/"
        f"v1/boards/{board_token}/jobs?content=true"
    )

    response = requests.get(
        url,
        timeout=20
    )

    response.raise_for_status()

    return response.json().get(
        "jobs",
        []
    )


def filter_greenhouse_jobs(jobs):
    matches = []

    for job in jobs:

        title = html.unescape(
            job.get("title", "")
        )

        content = html.unescape(
            job.get("content", "")
        )

        location = html.unescape(
            job.get(
                "location",
                {}
            ).get(
                "name",
                ""
            )
        )

        if not is_internship_title(title):
            continue

        if not is_relevant_job(
            title,
            content
        ):
            continue

        if not is_us_location(
            location,
            content
        ):
            continue

        job["relevance_score"] = (
            calculate_relevance(
                title,
                content
            )
        )

        matches.append(job)

    return matches


def search_greenhouse_boards(
    board_tokens
):
    all_matches = []

    for token in board_tokens:

        try:
            jobs = fetch_greenhouse_jobs(
                token
            )

            internships = (
                filter_greenhouse_jobs(
                    jobs
                )
            )

            print(
                f"Greenhouse {token}: "
                f"{len(jobs)} jobs, "
                f"{len(internships)} matches"
            )

            for job in internships:

                job["source_company"] = token
                job["source"] = "greenhouse"

                all_matches.append(job)

        except requests.RequestException as error:

            print(
                f"Greenhouse {token}: "
                f"failed - {error}"
            )

    return all_matches


# ============================================================
# LEVER
# ============================================================

def fetch_lever_jobs(company):
    url = (
        f"https://api.lever.co/v0/"
        f"postings/{company}?mode=json"
    )

    response = requests.get(
        url,
        timeout=20
    )

    response.raise_for_status()

    return response.json()


def lever_job_content(job):
    parts = []

    description = job.get(
        "descriptionPlain",
        ""
    )

    parts.append(description)

    for item in job.get(
        "lists",
        []
    ):
        parts.append(
            item.get(
                "text",
                ""
            )
        )

        parts.append(
            item.get(
                "content",
                ""
            )
        )

    return " ".join(parts)


def filter_lever_jobs(jobs):
    matches = []

    for job in jobs:

        title = html.unescape(
            job.get(
                "text",
                ""
            )
        )

        content = html.unescape(
            lever_job_content(job)
        )

        categories = job.get(
            "categories",
            {}
        )

        location = html.unescape(
            categories.get(
                "location",
                ""
            )
        )

        if not is_internship_title(title):
            continue

        if not is_relevant_job(
            title,
            content
        ):
            continue

        if not is_us_location(
            location,
            content
        ):
            continue

        matches.append(
            {
                "title": title,
                "content": content,
                "location": {
                    "name": location
                },
                "absolute_url": job.get(
                    "hostedUrl",
                    ""
                ),
                "relevance_score":
                    calculate_relevance(
                        title,
                        content
                    ),
            }
        )

    return matches


def search_lever_boards(
    companies
):
    all_matches = []

    for company in companies:

        try:
            jobs = fetch_lever_jobs(
                company
            )

            internships = (
                filter_lever_jobs(
                    jobs
                )
            )

            print(
                f"Lever {company}: "
                f"{len(jobs)} jobs, "
                f"{len(internships)} matches"
            )

            for job in internships:

                job["source_company"] = company
                job["source"] = "lever"

                all_matches.append(job)

        except requests.RequestException as error:

            print(
                f"Lever {company}: "
                f"failed - {error}"
            )

    return all_matches


# ============================================================
# COMBINED SEARCH
# ============================================================

def search_all_jobs(
    greenhouse_companies,
    lever_companies
):

    greenhouse_jobs = (
        search_greenhouse_boards(
            greenhouse_companies
        )
    )

    lever_jobs = (
        search_lever_boards(
            lever_companies
        )
    )

    all_jobs = (
        greenhouse_jobs
        + lever_jobs
    )

    # Remove duplicate URLs
    unique_jobs = {}

    for job in all_jobs:

        url = job.get(
            "absolute_url",
            ""
        )

        if url:
            unique_jobs[url] = job

    results = list(
        unique_jobs.values()
    )

    results.sort(
        key=lambda job: job.get(
            "relevance_score",
            0
        ),
        reverse=True
    )

    return results