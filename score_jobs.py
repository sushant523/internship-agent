from config import RESUME_PATH
from agents.resume_reader import read_resume
from agents.matcher import calculate_resume_match
from database import get_jobs, update_job_score


resume_text = read_resume(RESUME_PATH)

jobs = get_jobs()


print()
print("=" * 60)
print("RESUME MATCH RESULTS")
print("=" * 60)


for job in jobs:
    job_id = job[0]
    company = job[1]
    title = job[2]
    description = job[5]

    score = calculate_resume_match(
        resume_text,
        description
    )

    update_job_score(
        job_id,
        score
    )

    print()
    print(f"{score}%")
    print(f"{title}")
    print(f"{company}")


print()
print("All job scores updated.")