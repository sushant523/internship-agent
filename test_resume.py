from config import RESUME_PATH
from agents.resume_reader import read_resume

text = read_resume(RESUME_PATH)

print(text[:2000])