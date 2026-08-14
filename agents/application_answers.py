import json
from openai import OpenAI


def generate_application_answers(
    resume_text,
    title,
    company,
    location,
    description,
    prep=None
):
    client = OpenAI()

    prep_context = json.dumps(
        prep or {},
        ensure_ascii=False
    )

    prompt = f"""
You are helping an undergraduate student prepare truthful,
job-specific internship application answers.

Use ONLY the resume, job description, and existing preparation
context below.

Do not invent:
- work authorization
- citizenship
- sponsorship status
- security-clearance eligibility
- employment history
- projects
- technologies
- achievements

Return valid JSON with exactly these keys:

answers
review_flags

answers must be a list of objects.
Each object must contain:

question
answer
category

category must be one of:
"motivation"
"experience"
"technical"
"project"
"behavioral"
"additional"

Generate 5 to 8 useful application answers.

Include answers for these themes when relevant:

- Why are you interested in this company?
- Why are you interested in this role?
- Describe a relevant technical project.
- What technical skills or experience make you a good fit?
- Describe a time you communicated or collaborated effectively.
- Additional information / anything else you want us to know.

Rules for answers:

1. Keep each answer concise and application-ready.
2. Usually 80 to 180 words.
3. Use specific evidence from the resume.
4. Do not exaggerate experience.
5. Do not imply professional software engineering experience
   unless the resume actually shows it.
6. Do not fabricate cloud, security, networking, or framework
   experience.
7. If the job contains a hard eligibility question that cannot
   be answered from the resume, do NOT guess.

review_flags must be a list of short strings describing
questions that require the candidate's personal confirmation.

Examples:
- "Confirm current US work authorization."
- "Confirm whether sponsorship will be required."
- "Confirm security-clearance eligibility."
- "Confirm availability for internship dates."

JOB
Title: {title}
Company: {company}
Location: {location}

JOB DESCRIPTION
{description}

RESUME
{resume_text}

EXISTING APPLICATION PREP
{prep_context}
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
            "answers": [],
            "review_flags": [
                "The generated response could not be parsed."
            ]
        }