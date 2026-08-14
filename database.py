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
                    match_score
                FROM jobs
                ORDER BY match_score DESC
                """
            )

            return cursor.fetchall()


# ============================================================
# UPDATE RESUME MATCH SCORE
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

            # psycopg may already return JSONB as a Python dict.
            if isinstance(
                analysis,
                dict
            ):
                return analysis

            # Fallback in case it comes back as JSON text.
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