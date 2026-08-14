import os
import streamlit as st
import pandas as pd

from agents.job_finder import search_all_jobs
from agents.ai_matcher import analyze_job
from config import RESUME_PATH
from agents.resume_reader import read_resume
from agents.matcher import calculate_resume_match

from database import (
    initialize_database,
    add_job,
    get_jobs,
    update_job_score,
    update_job_status,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Internship Agent",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# SECRETS / ENVIRONMENT
# ============================================================

if "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# HEADER
# ============================================================

st.title("🤖 Internship Agent")

st.caption(
    "Find, rank, review, and track internship applications."
)


# ============================================================
# RESUME
# ============================================================

resume_text = read_resume(
    RESUME_PATH
)

if resume_text:
    st.success(
        "Resume loaded successfully."
    )
else:
    st.error(
        "Resume could not be loaded."
    )
    st.stop()


# ============================================================
# JOB REFRESH
# ============================================================

GREENHOUSE_COMPANIES = [
    "stripe",
    "datadog",
    "cloudflare",
    "mongodb",
    "robinhood",
    "affirm",
    "figma",
    "coinbase",
]

LEVER_COMPANIES = [
    "palantir",
]


if st.button(
    "🔄 Refresh Internship Listings",
    type="primary"
):

    with st.spinner(
        "Searching for internships..."
    ):

        found_jobs = search_all_jobs(
            GREENHOUSE_COMPANIES,
            LEVER_COMPANIES
        )

        for job in found_jobs:

            company = job.get(
                "source_company",
                "Unknown"
            )

            title = job.get(
                "title",
                "Unknown"
            )

            location = job.get(
                "location",
                {}
            ).get(
                "name",
                "Unknown"
            )

            url = job.get(
                "absolute_url",
                ""
            )

            description = job.get(
                "content",
                ""
            )

            add_job(
                company=company,
                title=title,
                location=location,
                url=url,
                description=description
            )

        st.success(
            f"Found {len(found_jobs)} internships!"
        )

        st.rerun()


# ============================================================
# LOAD JOBS
# ============================================================

jobs = get_jobs()

if not jobs:

    st.info(
        "No internships loaded yet. "
        "Click Refresh Internship Listings above."
    )

    st.stop()


# ============================================================
# SCORE UNSCORED JOBS
# ============================================================

for job in jobs:

    job_id = job[0]
    description = job[5] or ""
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


jobs = get_jobs()


# ============================================================
# DATAFRAME
# ============================================================

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
            df["Status"]
            == "Applied"
        ).sum()
    )
)

col3.metric(
    "Saved",
    int(
        (
            df["Status"]
            == "Saved"
        ).sum()
    )
)

col4.metric(
    "Skipped",
    int(
        (
            df["Status"]
            == "Skipped"
        ).sum()
    )
)


# ============================================================
# FILTERS
# ============================================================

st.subheader(
    "Filters"
)

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

st.subheader(
    "Internships"
)

display_df = filtered_df[
    [
        "Company",
        "Title",
        "Location",
        "Match Score",
        "Status",
        "URL"
    ]
].copy()

display_df["Company"] = (
    display_df["Company"]
    .astype(str)
    .str.title()
)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# DETAILED REVIEW
# ============================================================

st.subheader(
    "Review Jobs"
)


for _, row in filtered_df.iterrows():

    job_id = int(
        row["ID"]
    )

    title = row["Title"]

    company = str(
        row["Company"]
    ).title()

    location = row["Location"]

    score = row["Match Score"]

    status = row["Status"]

    url = row["URL"]

    description = row["Description"] or ""


    label = (
        f"{score:.1f}% — "
        f"{title} @ {company}"
    )


    with st.expander(
        label
    ):

        st.write(
            f"**Location:** "
            f"{location}"
        )

        st.write(
            f"**Status:** "
            f"{status}"
        )

        st.write(
            f"**Resume Match:** "
            f"{score:.1f}%"
        )


        # ====================================================
        # AI ANALYSIS
        # ====================================================

        if st.button(
            "🤖 Analyze with AI",
            key=f"ai-{job_id}"
        ):

            if "OPENAI_API_KEY" not in os.environ:

                st.error(
                    "OPENAI_API_KEY is not configured."
                )

            else:

                with st.spinner(
                    "Analyzing this internship..."
                ):

                    try:

                        analysis = analyze_job(
                            resume_text=resume_text,
                            title=title,
                            company=company,
                            location=location,
                            description=description
                        )

                        st.session_state[
                            f"analysis-{job_id}"
                        ] = analysis

                    except Exception as error:

                        st.error(
                            f"AI analysis failed: {error}"
                        )


        analysis = st.session_state.get(
            f"analysis-{job_id}"
        )


        if analysis:

            st.markdown(
                "### 🤖 AI Analysis"
            )

            ai_score = analysis.get(
                "match_score",
                0
            )

            verdict = analysis.get(
                "verdict",
                "N/A"
            )

            st.metric(
                "AI Match",
                f"{ai_score}%"
            )

            st.write(
                f"**Verdict:** "
                f"{verdict}"
            )


            strengths = analysis.get(
                "strengths",
                []
            )

            if strengths:

                st.markdown(
                    "**Strong Matches**"
                )

                for strength in strengths:

                    st.write(
                        f"✅ {strength}"
                    )


            gaps = analysis.get(
                "gaps",
                []
            )

            if gaps:

                st.markdown(
                    "**Potential Gaps**"
                )

                for gap in gaps:

                    st.write(
                        f"⚠️ {gap}"
                    )


            eligibility_notes = analysis.get(
                "eligibility_notes",
                []
            )

            if eligibility_notes:

                st.markdown(
                    "**Eligibility Notes**"
                )

                for note in eligibility_notes:

                    st.write(
                        f"• {note}"
                    )


            recommendation = analysis.get(
                "recommendation",
                ""
            )

            if recommendation:

                st.markdown(
                    "**Recommendation**"
                )

                st.write(
                    recommendation
                )


        # ====================================================
        # APPLICATION LINK
        # ====================================================

        if url:

            st.link_button(
                "Open Application",
                url
            )


        # ====================================================
        # JOB DESCRIPTION
        # ====================================================

        st.markdown(
            "### Job Description"
        )

        st.write(
            description
        )


        # ====================================================
        # STATUS BUTTONS
        # ====================================================

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