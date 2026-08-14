import os
import json
import psycopg


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    return database_url


def get_connection():
    return psycopg.connect(
        get_database_url()
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    id BIGSERIAL PRIMARY KEY,
                    company TEXT NOT NULL,
                    title TEXT NOT NULL,
                    location TEXT,
                    url TEXT UNIQUE,
                    description TEXT,
                    status TEXT DEFAULT 'New',
                    match_score DOUBLE PRECISION DEFAULT 0
                )
                """
            )

            cursor.execute(
                """
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS technical_match INTEGER
                """
            )

            cursor.execute(
                """
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS eligibility_status TEXT
                """
            )

            cursor.execute(
                """
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS ai_verdict TEXT
                """
            )

            cursor.execute(
                """
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS ai_analysis JSONB
                """
            )

            cursor.execute(
                """
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS application_prep JSONB
                """
            )

            cursor.execute(
                """
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS application_answers JSONB
                """
            )


# ============================================================
# ADD JOB
# ============================================================

def add_job(
    company,
    title,
    location,
    url,
    description
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO jobs
                (
                    company,
                    title,
                    location,
                    url,
                    description
                )
                VALUES (%s, %s, %s, %s, %s)

                ON CONFLICT (url)
                DO NOTHING
                """,
                (
                    company,
                    title,
                    location,
                    url,
                    description
                ),
            )


# ============================================================
# GET JOBS
# ============================================================

def get_jobs():
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    company,
                    title,
                    location,
                    url,
                    description,
                    status,
                    match_score,
                    technical_match,
                    eligibility_status,
                    ai_verdict
                FROM jobs
                ORDER BY
                    technical_match DESC NULLS LAST,
                    match_score DESC
                """
            )

            return cursor.fetchall()


# ============================================================
# UPDATE KEYWORD MATCH SCORE
# ============================================================

def update_job_score(
    job_id,
    score
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                UPDATE jobs
                SET match_score = %s
                WHERE id = %s
                """,
                (
                    score,
                    job_id
                ),
            )


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

def update_job_status(
    job_id,
    status
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                UPDATE jobs
                SET status = %s
                WHERE id = %s
                """,
                (
                    status,
                    job_id
                ),
            )


# ============================================================
# SAVE AI ANALYSIS
# ============================================================

def save_ai_analysis(
    job_id,
    analysis
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                UPDATE jobs
                SET
                    technical_match = %s,
                    eligibility_status = %s,
                    ai_verdict = %s,
                    ai_analysis = %s
                WHERE id = %s
                """,
                (
                    analysis.get(
                        "technical_match"
                    ),

                    analysis.get(
                        "eligibility_status"
                    ),

                    analysis.get(
                        "verdict"
                    ),

                    json.dumps(
                        analysis
                    ),

                    job_id
                ),
            )


# ============================================================
# LOAD AI ANALYSIS
# ============================================================

def get_ai_analysis(
    job_id
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT ai_analysis
                FROM jobs
                WHERE id = %s
                """,
                (
                    job_id,
                ),
            )

            row = cursor.fetchone()

            if not row:
                return None

            analysis = row[0]

            if isinstance(
                analysis,
                dict
            ):
                return analysis

            if isinstance(
                analysis,
                str
            ):
                try:
                    return json.loads(
                        analysis
                    )
                except json.JSONDecodeError:
                    return None

            return None


# ============================================================
# SAVE APPLICATION PREP
# ============================================================

def save_application_prep(
    job_id,
    prep
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                UPDATE jobs
                SET application_prep = %s
                WHERE id = %s
                """,
                (
                    json.dumps(
                        prep
                    ),
                    job_id
                ),
            )


# ============================================================
# LOAD APPLICATION PREP
# ============================================================

def get_application_prep(
    job_id
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT application_prep
                FROM jobs
                WHERE id = %s
                """,
                (
                    job_id,
                ),
            )

            row = cursor.fetchone()

            if not row:
                return None

            prep = row[0]

            if isinstance(
                prep,
                dict
            ):
                return prep

            if isinstance(
                prep,
                str
            ):
                try:
                    return json.loads(
                        prep
                    )
                except json.JSONDecodeError:
                    return None

            return None


# ============================================================
# SAVE APPLICATION ANSWERS
# ============================================================

def save_application_answers(
    job_id,
    answers
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                UPDATE jobs
                SET application_answers = %s
                WHERE id = %s
                """,
                (
                    json.dumps(
                        answers
                    ),
                    job_id
                ),
            )


# ============================================================
# LOAD APPLICATION ANSWERS
# ============================================================

def get_application_answers(
    job_id
):
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT application_answers
                FROM jobs
                WHERE id = %s
                """,
                (
                    job_id,
                ),
            )

            row = cursor.fetchone()

            if not row:
                return None

            answers = row[0]

            if isinstance(
                answers,
                dict
            ):
                return answers

            if isinstance(
                answers,
                str
            ):
                try:
                    return json.loads(
                        answers
                    )
                except json.JSONDecodeError:
                    return None

            return None