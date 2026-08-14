import json
from openai import OpenAI


def clean_text(value):
    """
    Enforce the no dash rule throughout generated writing.
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


def prepare_application(
    resume_text,
    title,
    company,
    location,
    description
):
    client = OpenAI()

    prompt = f"""
Prepare application material for an undergraduate student applying
to this internship.

Use only facts supported by the resume and job description.

Never invent experience, technologies, credentials, achievements,
citizenship, work authorization, sponsorship status, security
clearance eligibility, or personal history.

Return valid JSON with exactly these keys:

why_company
why_role
experience_summary
resume_points
likely_questions
cover_letter

why_company:
Write two to four sentences.

why_role:
Write two to four sentences.

experience_summary:
Write three to five sentences.

resume_points:
Return three to six specific points worth emphasizing.

likely_questions:
Return three to six plausible application questions based on the
posting.

cover_letter:
Write roughly 250 to 350 words.

VOICE AND STYLE

Write like a good human writer.

Think of a strong college essay written by an intelligent student,
then make it slightly more restrained because this is a professional
application.

The writing should have a person behind it.

Specific details should come before abstract claims.

Whenever possible, connect interest to an actual experience, project,
problem, class, responsibility, or moment from the resume.

Show first, then reflect.

Do not simply list qualifications.

Do not paraphrase the resume line by line.

Do not repeat language from the job description merely to prove that
the student read it.

Do not sound like marketing copy.

Vary sentence structure naturally.

Some sentences can be short.

Others can carry a thought for longer.

Transitions should feel natural rather than formulaic.

A little humor, curiosity, or personality is welcome when supported
by the material, but never force quirkiness.

The student should sound thoughtful, observant, curious, and grounded.

Do not make every paragraph end in a grand declaration.

Do not oversell.

Do not claim that every experience was transformative.

Avoid the typical application voice that sounds polished but empty.

NEVER USE THESE PHRASES

"I am thrilled"
"I am excited to apply"
"I am passionate about"
"I have always been passionate"
"I would be honored"
"I believe my background"
"I am confident that"
"perfect fit"
"unique opportunity"
"dynamic environment"
"fast paced environment"
"leverage my skills"
"aligns perfectly"
"strong alignment"
"proven track record"
"bring a unique perspective"
"make a meaningful impact"
"contribute to your team"
"take my skills to the next level"

Do not replace these with slightly different corporate clichés.

WHY COMPANY

Do not write a miniature advertisement for the company.

Find something concrete in the role or company's work that gives the
student a believable reason to care.

If there is not enough company specific information in the posting,
be modest. Do not invent enthusiasm.

WHY ROLE

Connect the work to things the student has actually done.

A project that caused curiosity is more interesting than saying the
student enjoys solving complex problems.

Explain what about the work attracts the student, not merely why the
student is qualified.

EXPERIENCE SUMMARY

Choose the two or three most relevant threads in the resume.

Connect them into a short narrative.

Do not turn this into a skills inventory.

COVER LETTER

The opening should not be:

"Dear Hiring Manager, I am writing to apply..."

Begin with an actual idea, experience, observation, project, or
reason the work caught the student's attention.

The middle should connect concrete experience to this role.

The ending should be restrained and confident.

Do not end with several sentences about excitement, gratitude, and
future contribution.

If a conventional greeting is needed, use:

"Dear Hiring Team,"

End simply with:

"Sincerely,
Sushant KC"

STRICT PUNCTUATION RULE

Never use hyphens.

Never use em dashes.

Never use en dashes.

Do not use dash punctuation at all.

If a phrase would normally contain a hyphen, rewrite the phrase.

For example:

Instead of "hands on experience", simply write a sentence such as
"I learned by building the project myself."

Instead of "real world problem", write "a problem I encountered
outside the classroom."

Do not allow a dash character anywhere in prose output.

ELIGIBILITY

If the posting contains a genuine hard eligibility blocker, do not
hide it.

Do not attempt to write around citizenship, security clearance,
graduation date, sponsorship, or work authorization requirements.

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
        result = json.loads(
            text
        )

        return clean_text(
            result
        )

    except json.JSONDecodeError:

        return {
            "why_company": "",
            "why_role": "",
            "experience_summary": "",
            "resume_points": [],
            "likely_questions": [],
            "cover_letter": "",
        }