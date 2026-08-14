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
    save_ai_analysis,
    get_ai_analysis,
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
# DATABASE
# ============================================================

initialize_database()


# ============================================================
# HEADER
# ============================================================

st.title("🤖 Internship Agent")

st.caption(
    "Find, rank, analyze, review, and track internship applications."
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
# JOB SOURCES
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


# ============================================================
# REFRESH JOBS
# ============================================================

if st.button(
    "🔄 Refresh Internship Listings",
    type="primary"
):

    with st.spinner(
        "Searching for internships..."
    ):

        try:

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
                f"Found {len(found_jobs)} matching internships."
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Job refresh failed: {error}"
            )


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


# Reload after scoring
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
    "AI Match",
    "Eligibility",
    "AI Verdict",
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
    "AI Analyzed",
    int(
        df["AI Match"]
        .notna()
        .sum()
    )
)


# ============================================================
# FILTERS
# ============================================================

st.subheader(
    "Filters"
)

filter_col1, filter_col2 = st.columns(2)

with filter_col1:

    minimum_score = st.slider(
        "Minimum Keyword Resume Match",
        min_value=0,
        max_value=100,
        value=20
    )


with filter_col2:

    status_filter = st.multiselect(
        "Application Status",
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
].copy()


# ============================================================
# MAIN JOB TABLE
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
        "AI Match",
        "Eligibility",
        "AI Verdict",
        "Status",
        "URL"
    ]
].copy()


display_df["Company"] = (
    display_df["Company"]
    .astype(str)
    .str.title()
)


display_df = display_df.rename(
    columns={
        "Match Score":
            "Keyword Match"
    }
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

    keyword_score = row[
        "Match Score"
    ]

    status = row[
        "Status"
    ]

    url = row[
        "URL"
    ]

    description = (
        row["Description"]
        or ""
    )

    stored_ai_match = row[
        "AI Match"
    ]

    stored_verdict = row[
        "AI Verdict"
    ]


    # ========================================================
    # EXPANDER LABEL
    # ========================================================

    if pd.notna(
        stored_ai_match
    ):

        label = (
            f"🤖 {int(stored_ai_match)}% AI — "
            f"{title} @ {company}"
        )

    else:

        label = (
            f"{keyword_score:.1f}% — "
            f"{title} @ {company}"
        )


    with st.expander(
        label
    ):

        # ====================================================
        # BASIC JOB INFO
        # ====================================================

        info1, info2, info3 = (
            st.columns(3)
        )

        info1.write(
            f"**Location:** {location}"
        )

        info2.write(
            f"**Status:** {status}"
        )

        info3.write(
            f"**Keyword Match:** "
            f"{keyword_score:.1f}%"
        )


        # ====================================================
        # LOAD SAVED AI ANALYSIS
        # ====================================================

        analysis_key = (
            f"analysis-{job_id}"
        )

        analysis = (
            st.session_state.get(
                analysis_key
            )
        )

        if analysis is None:

            try:

                analysis = get_ai_analysis(
                    job_id
                )

                if analysis:

                    st.session_state[
                        analysis_key
                    ] = analysis

            except Exception as error:

                st.warning(
                    f"Could not load saved "
                    f"AI analysis: {error}"
                )


        # ====================================================
        # FIRST AI ANALYSIS
        # ====================================================

        if analysis is None:

            if st.button(
                "🤖 Analyze with AI",
                key=f"ai-{job_id}",
                type="primary"
            ):

                if (
                    "OPENAI_API_KEY"
                    not in os.environ
                ):

                    st.error(
                        "OPENAI_API_KEY "
                        "is not configured."
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

                            save_ai_analysis(
                                job_id,
                                analysis
                            )

                            st.session_state[
                                analysis_key
                            ] = analysis

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"AI analysis failed: "
                                f"{error}"
                            )


        # ====================================================
        # DISPLAY AI ANALYSIS
        # ====================================================

        if analysis:

            st.markdown(
                "### 🤖 AI Analysis"
            )


            # =================================================
            # RE-ANALYZE
            # =================================================

            if st.button(
                "🔁 Re-analyze with AI",
                key=f"reanalyze-{job_id}"
            ):

                if (
                    "OPENAI_API_KEY"
                    not in os.environ
                ):

                    st.error(
                        "OPENAI_API_KEY "
                        "is not configured."
                    )

                else:

                    with st.spinner(
                        "Re-analyzing this "
                        "internship..."
                    ):

                        try:

                            new_analysis = (
                                analyze_job(
                                    resume_text=resume_text,
                                    title=title,
                                    company=company,
                                    location=location,
                                    description=description
                                )
                            )

                            save_ai_analysis(
                                job_id,
                                new_analysis
                            )

                            st.session_state[
                                analysis_key
                            ] = new_analysis

                            st.rerun()

                        except Exception as error:

                            st.error(
                                "AI re-analysis "
                                f"failed: {error}"
                            )


            technical_match = (
                analysis.get(
                    "technical_match",
                    0
                )
            )

            eligibility_status = (
                analysis.get(
                    "eligibility_status",
                    "UNCLEAR"
                )
            )

            verdict = (
                analysis.get(
                    "verdict",
                    "N/A"
                )
            )


            metric1, metric2, metric3 = (
                st.columns(3)
            )

            metric1.metric(
                "Technical Match",
                f"{technical_match}%"
            )

            metric2.metric(
                "Eligibility",
                eligibility_status
            )

            metric3.metric(
                "Verdict",
                verdict
            )


            # =================================================
            # STRENGTHS
            # =================================================

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


            # =================================================
            # TECHNICAL GAPS
            # =================================================

            gaps = analysis.get(
                "gaps",
                []
            )

            if gaps:

                st.markdown(
                    "**Technical Gaps**"
                )

                for gap in gaps:

                    st.write(
                        f"⚠️ {gap}"
                    )


            # =================================================
            # HARD REQUIREMENTS
            # =================================================

            hard_requirements = (
                analysis.get(
                    "hard_requirements",
                    []
                )
            )

            if hard_requirements:

                st.markdown(
                    "**Hard Requirements**"
                )

                for item in hard_requirements:

                    requirement = (
                        item.get(
                            "requirement",
                            ""
                        )
                    )

                    requirement_status = (
                        item.get(
                            "status",
                            "UNCLEAR"
                        )
                    )

                    evidence = (
                        item.get(
                            "evidence",
                            ""
                        )
                    )


                    if (
                        requirement_status
                        == "MET"
                    ):

                        icon = "✅"

                    elif (
                        requirement_status
                        == "NOT MET"
                    ):

                        icon = "❌"

                    else:

                        icon = "❓"


                    st.write(
                        f"{icon} "
                        f"**{requirement}** "
                        f"— "
                        f"{requirement_status}"
                    )

                    if evidence:

                        st.caption(
                            evidence
                        )


            # =================================================
            # PREFERRED QUALIFICATIONS
            # =================================================

            preferred = analysis.get(
                "preferred_qualifications",
                []
            )

            if preferred:

                st.markdown(
                    "**Preferred Qualifications**"
                )

                for item in preferred:

                    qualification = (
                        item.get(
                            "qualification",
                            ""
                        )
                    )

                    preferred_status = (
                        item.get(
                            "status",
                            ""
                        )
                    )

                    st.write(
                        f"• {qualification} "
                        f"— {preferred_status}"
                    )


            # =================================================
            # RECOMMENDATION
            # =================================================

            recommendation = (
                analysis.get(
                    "recommendation",
                    ""
                )
            )

            if recommendation:

                st.markdown(
                    "**Recommendation**"
                )

                st.write(
                    recommendation
                )


        # ====================================================
        # APPLICATION
        # ====================================================

        st.markdown("---")

        if url:

            st.link_button(
                "🚀 Open Application",
                url
            )


        # ====================================================
        # JOB DESCRIPTION
        # ====================================================

        with st.expander(
            "View Full Job Description"
        ):

            st.write(
                description
            )


        # ====================================================
        # APPLICATION STATUS
        # ====================================================

        st.markdown(
            "**Application Status**"
        )

        col1, col2, col3 = (
            st.columns(3)
        )


        if col1.button(
            "⭐ Save",
            key=f"save-{job_id}"
        ):

            update_job_status(
                job_id,
                "Saved"
            )

            st.rerun()


        if col2.button(
            "✅ Applied",
            key=f"applied-{job_id}"
        ):

            update_job_status(
                job_id,
                "Applied"
            )

            st.rerun()


        if col3.button(
            "⏭️ Skip",
            key=f"skip-{job_id}"
        ):

            update_job_status(
                job_id,
                "Skipped"
            )

            st.rerun()