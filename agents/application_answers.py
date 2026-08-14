import json
from openai import OpenAI


def clean_text(value):
    """
    Enforce the no dash rule throughout generated answers.
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
Draft truthful internship application responses for the student
whose resume appears below.

Use only the resume, job description, and existing preparation
context.

Never invent:

work authorization
citizenship
sponsorship status
security clearance eligibility
employment history
projects
technologies
academic achievements
personal experiences

Return valid JSON with exactly these keys:

answers
review_flags

answers must be a list of objects.

Each object must contain:

question
answer
category

category must be exactly one of:

"motivation"
"experience"
"technical"
"project"
"behavioral"
"additional"

Generate five to eight useful responses.

Include these subjects when relevant:

Why this company?

Why this role?

Describe a relevant project.

What technical experience would you bring?

Describe a time you worked or communicated with other people.

Is there anything else you want the employer to know?

VOICE

Write in first person as the student.

The answer should sound like a real college student who happens to
write well.

Think college essay voice compressed into an internship response.

Specific before abstract.

Experience before conclusion.

Show something, then explain what it meant.

Do not begin every answer with a direct thesis.

Sometimes begin with a project, moment, problem, realization, or
small detail.

Use the student's actual experiences as material rather than turning
their skills section into prose.

The writing can be reflective without becoming sentimental.

It can be confident without performing confidence.

It can show personality without trying to be clever.

Vary sentence length.

Allow occasional short sentences when they help rhythm.

Do not make each paragraph structurally identical.

Avoid generic openings and generic conclusions.

Do not repeat the same anecdote in every response.

If one answer discusses a technical project, another answer should
prefer a different part of the student's life when the resume
supports it.

When discussing work with people, use actual client service,
translation, food service, volunteering, teamwork, or other
human experience from the resume when relevant.

Do not force every answer back to coding.

The reader should come away knowing a person, not just a list of
technologies.

AVOID APPLICATION CLICHÉS

Never write:

"I am thrilled"
"I am excited"
"I am passionate about"
"I have always been passionate about"
"I believe I am a strong fit"
"I believe my background"
"I am confident"
"this opportunity aligns"
"perfectly aligns"
"unique opportunity"
"dynamic environment"
"fast paced"
"leverage"
"proven track record"
"make an impact"
"meaningful impact"
"contribute my skills"
"hone my skills"
"take my skills to the next level"

Do not replace these phrases with synonyms that accomplish the same
empty function.

If a sentence could apply to five hundred other applicants, rewrite
it with something specific.

ANSWER LENGTH

Most responses should be around 90 to 170 words.

Do not stretch a simple answer to reach a word count.

If a question calls for a shorter answer, write less.

QUALITY TEST

Before returning each answer, silently ask:

Could a stranger with a similar major have written this?

If yes, make it more specific.

Does this sound as though the student is trying to impress the
reader?

If yes, make it quieter.

Does the answer merely tell instead of giving evidence?

If yes, add an actual detail from the resume.

Does every sentence sound equally polished?

If yes, vary the rhythm.

STRICT PUNCTUATION RULE

Never use hyphens.

Never use em dashes.

Never use en dashes.

Never use dash punctuation.

Rewrite any sentence that would require one.

review_flags must contain only items that genuinely need the
student's personal confirmation.

Examples include:

"Confirm current United States work authorization."

"Confirm whether future sponsorship will be required."

"Confirm security clearance eligibility."

"Confirm availability for the internship dates."

Never generate an answer to one of these questions by guessing.

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
        result = json.loads(
            text
        )

        return clean_text(
            result
        )

    except json.JSONDecodeError:

        return {
            "answers": [],
            "review_flags": [
                "The generated response could not be read correctly."
            ]
        }