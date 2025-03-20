import sys
import os

import openai
from dotenv import load_dotenv
load_dotenv()

CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")
SEEK_EMAIL = os.getenv('SEEK_EMAIL')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CV_TEXT = os.getenv("CV_TEXT")
OPENAI_CLIENT = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
# RESUME_TEXT="18/3/25 - Resume-sample.pdf" #test
RESUME_TEXT=os.getenv('RESUME_TEXT')


# Use environment variables
db_url = os.getenv('DATABASE_URL', 'sqlite:///data/jobs.db')