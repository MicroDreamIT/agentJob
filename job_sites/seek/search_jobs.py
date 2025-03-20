from datetime import datetime
from selenium.common import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .apply_on_job import apply_on_job, apply_step_1_resume_cover_letter, apply_step_2_employer_questions
from core.database import Job, open_session, close_session


def search_jobs(driver, what="full-stack-developer", days=1):
    base_url = "https://www.seek.com.au"
    page_number = 1
    session = open_session()

    #test_begin
    # cover_letter = "I am a professional HR assistant helping to craft cover letters."
    # driver.get('https://www.seek.com.au/job/82897618/apply/role-requirements?sol=0c58f7151b4c526d7e0a8ba11f2db9ff1b81f5df')
    # # job_detail_returns = apply_on_job(driver, '82897618')
    # success_if = apply_step_1_resume_cover_letter(driver, cover_letter)
    # if success_if:
    #     apply_step_2_employer_questions(driver)

    # return True
    #test_end

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
    wait = WebDriverWait(driver, 15)
    job_list = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-automation='normalJob'][data-job-id]")))

    for job in job_list:
        try:
            job_id = job.get_attribute("data-job-id")
            job_title_link = job.find_element(By.CSS_SELECTOR, "a[data-automation='jobTitle']")
            job_title = job_title_link.text
            job_link = job_title_link.get_attribute("href")

            if job_id:
                process_job(session, driver, job_id, job_title, job_link)
            else:
                raise ValueError("Job ID not found or is None")

        except Exception as e:
            print(f"Error processing job: {e}")
            print(f"Job HTML: {job}")  # Print part of the job's HTML for debugging
            continue


def process_job(session, driver, job_id, job_title, job_link):
    existing_job = session.query(Job).filter_by(provider='SEEK', provider_id=job_id).first()
    if not existing_job:
        print(f"➡️Processing job: {job_title}, job_id: {job_id}")
        job_detail_returns = apply_on_job(driver, job_id, job_link)
        is_quick_apply_available = job_detail_returns[0]
        cover_letter = job_detail_returns[1]
        new_job = Job(
            provider='SEEK',
            provider_id=job_id,
            title=job_title,
            link=job_link,
            is_quick_apply=is_quick_apply_available,
            cover_letter=cover_letter,
            applied_on=datetime.utcnow()
        )
        session.add(new_job)
        session.commit()

        print(f"✅ Stored job: {job_title}, Quick Apply: {is_quick_apply_available}")
    else:
        print(f"Job '{existing_job.title}' already processed.")


def has_next_page(driver):
    try:
        driver.find_element(By.XPATH, "//a[@aria-label='Next']")
        return True
    except NoSuchElementException:
        return False