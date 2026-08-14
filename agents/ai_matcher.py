import json
from openai import OpenAI


def analyze_job(resume_text, title, company, location, description):
    client = OpenAI()

    prompt = f"""
You are evaluating an internship for a student.

Use ONLY the resume and job description below.
Do not invent experience, skills, eligibility, or credentials.

Return valid JSON with exactly these keys:

match_score
verdict
strengths
gaps
eligibility_notes
recommendation

Rules:
- match_score: integer from 0 to 100
- verdict: one of "STRONG APPLY", "APPLY", "MAYBE", "LOW PRIORITY"
- strengths: list of short strings
- gaps: list of short strings
- eligibility_notes: list of short strings
- recommendation: 2-4 sentence explanation
- Distinguish required qualifications from preferred qualifications.
- Do not assume work authorization or sponsorship eligibility unless explicitly supported.
- Do not penalize heavily for preferred qualifications.
- Focus on internship-level expectations.

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

    # Handle accidental markdown fencing
    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "")
        text = text.strip()

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        return {
            "match_score": 0,
            "verdict": "MAYBE",
            "strengths": [],
            "gaps": [],
            "eligibility_notes": [],
            "recommendation": (
                "The AI analysis could not be parsed correctly."
            ),
        }