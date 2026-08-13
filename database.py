import sqlite3
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

DB_PATH = (
    Path(__file__).resolve().parent
    / "data"
    / "applications.db"
)


# ============================================================
# CONNECTION
# ============================================================

def get_connection():
    # Streamlit Cloud may start without the data folder.
    # Create it automatically if it doesn't exist.
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(DB_PATH)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

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


# ============================================================
# GET JOBS
# ============================================================

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


# ============================================================
# UPDATE MATCH SCORE
# ============================================================

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


# ============================================================
# UPDATE APPLICATION STATUS
# ============================================================

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