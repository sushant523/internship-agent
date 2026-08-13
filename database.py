import os
import psycopg


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