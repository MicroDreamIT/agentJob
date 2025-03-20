import os
import openai
from dotenv import load_dotenv

def load_environment():
    """ Load the appropriate environment variables based on the deployment context. """
    if os.getenv('APP_ENV') == 'local':
        dotenv_path = '.env'
    else:
        dotenv_path = '.testenv'
    load_dotenv(dotenv_path=dotenv_path)

# Call the function to load the environment at the start
load_environment()

# Initialize OpenAI Client with API Key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Missing OPENAI_API_KEY in the environment variables.")
OPENAI_CLIENT = openai.Client(api_key=OPENAI_API_KEY)

# Retrieve other environment variables
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")
SEEK_EMAIL = os.getenv('SEEK_EMAIL')
if not SEEK_EMAIL:
    raise ValueError("Missing SEEK_EMAIL in the environment variables.")
CV_TEXT = os.getenv("CV_TEXT")
RESUME_TEXT = os.getenv('RESUME_TEXT')  # Provide a default path if not set

# Database URL with a default value
db_url = os.getenv('DATABASE_URL')

# Usage of variables for clarity
print(f"Using Chrome Driver at: {CHROME_DRIVER_PATH}")
print(f"Database URL: {db_url}")
