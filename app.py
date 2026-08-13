import streamlit as st
import pandas as pd

from config import RESUME_PATH
from agents.resume_reader import read_resume
from agents.matcher import calculate_resume_match
from database import (
    get_jobs,
    update_job_score,
    update_job_status,
)


st.set_page_config(
    page_title="Internship Agent",
    page_icon="🤖",
    layout="wide"
)


st.title("🤖 Internship Agent")
st.caption(
    "Find, rank, review, and track internship applications."
)


resume_text = read_resume(RESUME_PATH)

if resume_text:
    st.success("Resume loaded successfully.")
else:
    st.error("Resume could not be loaded.")
    st.stop()


jobs = get_jobs()


# Score any jobs that still have score 0
for job in jobs:
    job_id = job[0]
    description = job[5]
    match_score = job[7]

    if match_score == 0:
        score = calculate_resume_match(
            resume_text,
            description
        )

        update_job_score(
            job_id,
            score
        )


# Reload after scoring
jobs = get_jobs()


columns = [
    "ID",
    "Company",
    "Title",
    "Location",
    "URL",
    "Description",
    "Status",
    "Match Score",
]


df = pd.DataFrame(
    jobs,
    columns=columns
)


# ============================================================
# SUMMARY
# ============================================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Jobs Found",
    len(df)
)

col2.metric(
    "Applied",
    int(
        (
            df["Status"] == "Applied"
        ).sum()
    )
)

col3.metric(
    "Saved",
    int(
        (
            df["Status"] == "Saved"
        ).sum()
    )
)

col4.metric(
    "Skipped",
    int(
        (
            df["Status"] == "Skipped"
        ).sum()
    )
)


# ============================================================
# FILTERS
# ============================================================

st.subheader("Filters")


minimum_score = st.slider(
    "Minimum Resume Match",
    min_value=0,
    max_value=100,
    value=20
)


status_filter = st.multiselect(
    "Status",
    [
        "New",
        "Saved",
        "Applied",
        "Skipped"
    ],
    default=[
        "New",
        "Saved",
        "Applied"
    ]
)


filtered_df = df[
    (
        df["Match Score"]
        >= minimum_score
    )
    &
    (
        df["Status"].isin(
            status_filter
        )
    )
]


# ============================================================
# JOB TABLE
# ============================================================

st.subheader("Internships")


st.dataframe(
    filtered_df[
        [
            "Company",
            "Title",
            "Location",
            "Match Score",
            "Status",
            "URL"
        ]
    ],
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DETAILED REVIEW
# ============================================================

st.subheader("Review Jobs")


for _, row in filtered_df.iterrows():

    job_id = int(row["ID"])

    title = row["Title"]
    company = row["Company"]
    location = row["Location"]
    score = row["Match Score"]
    status = row["Status"]
    url = row["URL"]
    description = row["Description"]


    label = (
        f"{score:.1f}% — "
        f"{title} @ {company}"
    )


    with st.expander(label):

        st.write(
            f"**Location:** {location}"
        )

        st.write(
            f"**Status:** {status}"
        )

        st.write(
            f"**Resume Match:** "
            f"{score:.1f}%"
        )


        if url:
            st.link_button(
                "Open Application",
                url
            )


        st.markdown(
            "### Job Description"
        )

        st.write(
            description
        )


        col1, col2, col3 = (
            st.columns(3)
        )


        if col1.button(
            "Save",
            key=f"save-{job_id}"
        ):
            update_job_status(
                job_id,
                "Saved"
            )

            st.rerun()


        if col2.button(
            "Applied",
            key=f"applied-{job_id}"
        ):
            update_job_status(
                job_id,
                "Applied"
            )

            st.rerun()


        if col3.button(
            "Skip",
            key=f"skip-{job_id}"
        ):
            update_job_status(
                job_id,
                "Skipped"
            )

            st.rerun()