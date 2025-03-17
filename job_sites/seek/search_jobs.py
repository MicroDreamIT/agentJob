from datetime import datetime
from selenium.common import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .apply_on_job import apply_on_job
from core.database import Job, open_session, close_session


def search_jobs(driver, what="full-stack-developer", days=1):
    base_url = "https://www.seek.com.au"
    page_number = 1
    session = open_session()

    while True:
        query = f"{what}-jobs?daterange={days}&page={page_number}"
        full_url = f"{base_url}/{query}"
        driver.get(full_url)
        print(f"Scanning page {page_number}...")
        process_job_listings(driver, session)

        page_number += 1
        if not has_next_page(driver):
            break

    close_session(session)


def process_job_listings(driver, session):
    wait = WebDriverWait(driver, 20)
    job_list = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-automation='normalJob']")))

    for job in job_list:
        job_id = job.get_attribute("data-job-id")
        job_title_link = job.find_element(By.CSS_SELECTOR, "a[data-automation='jobTitle']")
        job_title = job_title_link.text
        job_link = job_title_link.get_attribute("href")
        process_job(session, driver, job_id, job_title, job_link)

def process_job(session, driver, job_id, job_title, job_link):
    existing_job = session.query(Job).filter_by(provider='SEEK', provider_id=job_id).first()
    if not existing_job:
        application_status = apply_on_job(driver, job_link)

        new_job = Job(
            provider='SEEK',
            provider_id=job_id,
            title=job_title,
            link=job_link,
            is_quick_apply=(application_status == 'quick_apply')
        )

        if application_status in ['quick_apply', 'external_apply']:
            new_job.applied_on = datetime.utcnow()

        session.add(new_job)
        session.commit()
        print(f"Processed new job: {job_title}, Quick Apply: {new_job.is_quick_apply}")
    else:
        print(f"Job '{existing_job.title}' already processed.")

def has_next_page(driver):
    try:
        driver.find_element(By.XPATH, "//a[@aria-label='Next']")
        return True
    except NoSuchElementException:
        return False