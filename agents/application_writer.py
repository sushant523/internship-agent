import json
from openai import OpenAI


def prepare_application(
    resume_text,
    title,
    company,
    location,
    description
):
    client = OpenAI()

    prompt = f"""
You are preparing internship application materials
for an undergraduate student.

Use ONLY the resume and job description below.
Do not invent experience, skills, credentials,
citizenship, work authorization, or achievements.

Return valid JSON with exactly these keys:

why_company
why_role
experience_summary
resume_points
likely_questions
cover_letter

Rules:

- why_company:
  2-4 sentences, specific to the company and role.

- why_role:
  2-4 sentences explaining why the candidate fits
  and is interested in this type of work.

- experience_summary:
  3-5 sentences summarizing the most relevant
  background from the resume.

- resume_points:
  list of 3-6 concrete resume bullets or themes
  that should be emphasized for this application.

- likely_questions:
  list of 3-6 likely application questions.
  These must be plausible based on the posting.

- cover_letter:
  concise internship cover letter.
  Approximately 250-350 words.
  No invented facts.
  Do not claim technologies the candidate
  has not used.
  Do not claim work authorization,
  sponsorship status, citizenship,
  or security-clearance eligibility.

If the posting contains a hard eligibility blocker,
do not hide it. Keep the writing useful but truthful.

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
        return json.loads(text)

    except json.JSONDecodeError:
        return {
            "why_company": "",
            "why_role": "",
            "experience_summary": "",
            "resume_points": [],
            "likely_questions": [],
            "cover_letter": "",
        }