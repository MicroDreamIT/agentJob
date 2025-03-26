# get input
import time

from sqlalchemy.orm import Session

from core.config import CHROME_DRIVER_PATH
from core.database import Job, engine, FailedJob
from job_sites.for_ai_process.process_cover_letter_openai import process_cover_letter_openai
from job_sites.helpers.get_provider_link import get_provider_and_link
from job_sites.seek.apply_on_job import (
    apply_step_1_resume_cover_letter,
    check_for_answer_questions_text,
    apply_step_2_employer_questions,
    update_seek_profile,
    review_and_submit)

from job_sites.seek.click_quick_apply_button import click_quick_apply_button
from job_sites.seek.get_job_description import get_job_description
from job_sites.seek.is_seek import check_for_redirection
from job_sites.seek.login import login_to_seek
from sqlalchemy import select
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from job_sites.helpers.minimize_chrome import minimize_chrome

if __name__ == "__main__":
    table_name = input("Enter the table name: 1. Job 2. FailedJob: ")
    if table_name == '1':
        table = Job
    else:
        table = FailedJob

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    logged_in_driver = login_to_seek(driver)
    if logged_in_driver:
        session = Session(engine)

        if table == Job:
            rows = select(Job).filter(
                Job.is_quick_apply == 0,
                Job.provider == 'SEEK'
            )
        else:
            rows = select(FailedJob).filter(
                FailedJob.provider == 'SEEK'
            )

        for fail_job in session.scalars(rows):
            print(f"➡️Processing job: {fail_job.link}, job_id: {fail_job.provider_id}")
            seek_apply_url = f"https://www.seek.com.au/job/{fail_job.provider_id}/apply/"
            logged_in_driver.get(
                seek_apply_url
            )
            on_seek, final_url = check_for_redirection(logged_in_driver, seek_apply_url)
            if on_seek:
                # click_quick_apply_button(logged_in_driver)
                job_description = get_job_description(logged_in_driver)
                if not job_description:
                    print("❌ Failed to get job description")
                    continue
                cover_letter = process_cover_letter_openai(job_description)
                success = apply_step_1_resume_cover_letter(logged_in_driver, cover_letter)
                if check_for_answer_questions_text(logged_in_driver):
                    print("✅ Step 2 in progress...")
                    apply_step_2_employer_questions(logged_in_driver)
                    # input('check everything ...')

                time.sleep(3)
                print("➡️ update_seek_profile in progress...")
                update_seek_profile(logged_in_driver)
                time.sleep(3)
                print("➡️ review_and_submit in progress...")
                review_and_submit(logged_in_driver)

                # click quick apply button
                # get the description click on -> view job description
                # click close job description
                # click write cover letter
                # generate cover letter

                try:
                    if table == Job:
                        fail_job.is_quick_apply = 1
                    else:
                        session.delete(fail_job)
                    session.commit()
                except Exception as e:
                    print(f"Error applying for job: {e}")
                    stmt = select(FailedJob).where(FailedJob.provider_id == fail_job.provider_id)
                    failed_job_is_exist = session.scalars(stmt).one()
                    if not failed_job_is_exist:
                        failed_job_save = FailedJob(
                            provider='SEEK',
                            provider_id=fail_job.provider_id,
                            link=fail_job.link,
                            error_message=str(e)
                        )
                        session.add(failed_job_save)
                        session.commit()

            else:
                fail_job.provider, fail_job.link = get_provider_and_link(final_url)
                fail_job.is_quick_apply = 0
                session.commit()
        # Close the session
        session.close()
