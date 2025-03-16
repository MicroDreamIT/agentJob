import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the DATABASE_URL from the environment variable or use a default value
db_url = os.getenv('DATABASE_URL', 'sqlite:///data/jobs.db')

# This URL will be used elsewhere in your project to connect to the database