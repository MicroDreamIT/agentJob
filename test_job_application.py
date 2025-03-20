import os

import openai
from dotenv import load_dotenv
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from job_sites.seek.apply_on_job import apply_step_2_employer_questions, apply_step_1_resume_cover_letter
from job_sites.seek.login import login_to_seek



def run_test_application():
    """
    Logs into Seek, opens a job application link, and applies Step 1.
    """
    driver = webdriver.Chrome()
    cover_letter = "Hello, I am a software engineer with 5 years of experience. I am excited to apply for this role."

    # Step 1: Log in to Seek
    print("🔑 Logging into Seek...")
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

    if not api_key:
        raise ValueError("❌ ERROR: OPENAI_API_KEY is missing in test execution!")

    driver = login_to_seek()

    if not driver:
        print("❌ Failed to log in. Exiting test.")
        return
    driver.get("https://www.seek.com.au/job/82897618/apply/role-requirements?sol=0c58f7151b4c526d7e0a8ba11f2db9ff1b81f5df")

    # Wait for page to load completely
    wait = WebDriverWait(driver, 15)
    success = apply_step_1_resume_cover_letter(driver, cover_letter)
    if success:
        print("🚀 Proceeding to Step 2: Employer Questions...")
        apply_step_2_employer_questions(driver)
    else:
        print("⚠️ Stopping test as Step 1 failed.")

    driver.quit()  # Close the browser session

# Run the full test
run_test_application()