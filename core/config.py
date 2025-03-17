import sys
import os

from dotenv import load_dotenv

CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")
SEEK_EMAIL = "cristianaanna@gmail.com"

load_dotenv()

# Use environment variables
db_url = os.getenv('DATABASE_URL', 'sqlite:///data/jobs.db')