import os
from dotenv import load_dotenv, find_dotenv
import backend.services as services

load_dotenv(find_dotenv())

try:
    print("Testing generate_syllabus...")
    course = services.generate_syllabus("Public Speaking", 3, "2 hours/week")
    print(len(course.modules))
    print(course.modules[0].title)
except Exception as e:
    print(f"FAILED: {e}")
