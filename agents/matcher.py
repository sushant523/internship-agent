import re


STOP_WORDS = {
    "the", "and", "or", "a", "an", "to", "of", "in", "for", "with",
    "on", "is", "are", "be", "as", "at", "by", "from", "this", "that",
    "will", "you", "your", "our", "we", "their", "they", "have", "has",
    "using", "use", "used", "job", "role", "team", "work", "working",
}


IMPORTANT_SKILLS = {
    "python": 8,
    "c++": 7,
    "javascript": 7,
    "sql": 8,
    "git": 6,
    "rest": 6,
    "api": 6,
    "database": 6,
    "databases": 6,
    "oop": 5,
    "security": 8,
    "cybersecurity": 9,
    "network": 8,
    "networking": 8,
    "cloud": 7,
    "linux": 7,
    "backend": 6,
    "software": 7,
    "machine": 5,
    "learning": 5,
    "data": 5,
    "llm": 5,
    "rag": 5,
}


def tokenize(text):
    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.-]*",
        (text or "").lower()
    )

    return {
        word
        for word in words
        if len(word) > 2
        and word not in STOP_WORDS
    }


def calculate_resume_match(resume_text, job_description):
    resume_terms = tokenize(resume_text)
    job_terms = tokenize(job_description)

    if not job_terms:
        return 0.0

    overlap = resume_terms & job_terms

    base_score = (
        len(overlap)
        / len(job_terms)
    ) * 100

    bonus = 0

    for skill, weight in IMPORTANT_SKILLS.items():
        if (
            skill in resume_terms
            and skill in job_terms
        ):
            bonus += weight

    final_score = base_score + bonus

    return round(
        min(final_score, 100),
        1
    )