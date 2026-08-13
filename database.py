import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "data" / "applications.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            url TEXT UNIQUE,
            description TEXT,
            status TEXT DEFAULT 'New',
            match_score REAL DEFAULT 0
        )
        """
    )

    conn.commit()
    conn.close()


def add_job(
    company,
    title,
    location,
    url,
    description
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO jobs
        (
            company,
            title,
            location,
            url,
            description
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            company,
            title,
            location,
            url,
            description
        ),
    )

    conn.commit()
    conn.close()


def get_jobs():
    conn = get_connection()
    cursor = conn.cursor()

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

    jobs = cursor.fetchall()

    conn.close()

    return jobs


def update_job_score(
    job_id,
    score
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE jobs
        SET match_score = ?
        WHERE id = ?
        """,
        (
            score,
            job_id
        ),
    )

    conn.commit()
    conn.close()


def update_job_status(
    job_id,
    status
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE jobs
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            job_id
        ),
    )

    conn.commit()
    conn.close()