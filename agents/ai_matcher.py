import json
from openai import OpenAI


def clean_text(value):
    """
    Remove dash punctuation from generated prose.
    This applies recursively to strings inside lists
    and dictionaries as well.
    """

    if isinstance(value, str):
        return (
            value
            .replace("—", ",")
            .replace("–", ",")
            .replace("-", " ")
        )

    if isinstance(value, list):
        return [
            clean_text(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: clean_text(item)
            for key, item in value.items()
        }

    return value


def analyze_job(
    resume_text,
    title,
    company,
    location,
    description
):
    client = OpenAI()

    prompt = f"""
Evaluate this internship for the student whose resume appears below.

Your job is not to sell the student to the employer and not to speak
like a recruiter. Think like a thoughtful adviser who knows the
student well and is helping them decide whether the application is
worth their time.

Use only information supported by the resume and job description.
Never invent experience, skills, credentials, citizenship, work
authorization, sponsorship status, security clearance eligibility,
or achievements.

Return valid JSON with exactly these keys:

technical_match
eligibility_status
hard_requirements
preferred_qualifications
strengths
gaps
verdict
recommendation

technical_match:
An integer from 0 through 100.

This score measures technical and academic fit only.

Do not reduce technical_match because of citizenship, sponsorship,
security clearance, location, graduation year, or other eligibility
issues. Those belong in eligibility_status and hard_requirements.

eligibility_status must be exactly one of:

"ELIGIBLE"
"LIKELY ELIGIBLE"
"UNCLEAR"
"LIKELY INELIGIBLE"

hard_requirements:
A list of objects.

Each object must contain:

requirement
status
evidence

status must be exactly one of:

"MET"
"NOT MET"
"UNCLEAR"

preferred_qualifications:
A list of objects.

Each object must contain:

qualification
status

status must be exactly one of:

"MATCH"
"PARTIAL"
"MISSING"

strengths:
A list of concrete reasons the student's background connects to the
role.

gaps:
A list of meaningful technical gaps only.

Do not create a gap merely because a technology appears somewhere in
the posting.

verdict must be exactly one of:

"STRONG APPLY"
"APPLY"
"MAYBE"
"LOW PRIORITY"
"DO NOT APPLY"

recommendation:
Write two to four sentences directly to the student.

WRITING VOICE

Write like an intelligent person speaking to another intelligent
person.

Do not sound like a recruiter, career coach, corporate memo, or AI
assistant.

The recommendation should feel closer to thoughtful college essay
prose than business copy.

Be specific before being abstract.

Use details from the resume and posting instead of broad claims.

Allow some personality when it occurs naturally.

Vary sentence length.

A short sentence is fine.

Reflection is better than promotion.

Do not repeatedly call the student "the candidate."

Speak directly using "you" when writing the recommendation.

Do not use corporate filler such as:

"leverage your skills"
"strong alignment"
"unique opportunity"
"dynamic environment"
"passionate about"
"excellent fit"
"well positioned"
"demonstrates a strong ability"
"your background aligns"
"proven track record"

Avoid unnecessary adjectives.

Do not make everything sound impressive.

If something is a real weakness or blocker, simply say so.

STRICT PUNCTUATION RULE

Do not use hyphens.

Do not use em dashes.

Do not use en dashes.

Restructure the sentence instead.

Do not use dash punctuation anywhere in prose values returned in
the JSON.

EVALUATION RULES

1. Separate technical fit from eligibility.

2. Projects and coursework are legitimate evidence for an
undergraduate internship.

3. Lack of previous professional software engineering experience
should not automatically cause a low technical score.

4. Distinguish required qualifications from preferred ones.

5. Do not heavily penalize missing preferred technologies.

6. If the employer explicitly says specific programming languages do
not matter, respect that statement.

7. If a required graduation date clearly conflicts with the resume,
mark it NOT MET.

8. If security clearance eligibility cannot be determined from the
resume, mark it UNCLEAR rather than NOT MET.

9. Never infer citizenship or work authorization.

10. A student can receive a high technical_match while receiving
LOW PRIORITY because of a genuine eligibility blocker.

11. Technical fit should consider education, programming, projects,
data structures, algorithms, databases, APIs, software engineering
fundamentals, networking, security, communication, and other areas
only when relevant to this specific role.

JOB

Title: {title}
Company: {company}
Location: {location}

JOB DESCRIPTION

{description}

RESUME

{resume_text}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    text = response.output_text.strip()

    if text.startswith("```"):
        text = text.replace(
            "```json",
            "",
            1
        )

        text = text.replace(
            "```",
            ""
        ).strip()

    try:
        result = json.loads(text)

        return clean_text(
            result
        )

    except json.JSONDecodeError:

        return {
            "technical_match": 0,
            "eligibility_status": "UNCLEAR",
            "hard_requirements": [],
            "preferred_qualifications": [],
            "strengths": [],
            "gaps": [],
            "verdict": "MAYBE",
            "recommendation": (
                "The assessment could not be read correctly. "
                "Try running it again."
            ),
        }