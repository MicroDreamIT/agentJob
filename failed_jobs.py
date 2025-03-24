# get input
import time

from sqlalchemy.orm import Session

from core.database import Job, engine, FailedJob
from job_sites.for_ai_process.process_cover_letter_openai import process_cover_letter_openai
from job_sites.seek.apply_on_job import (
    apply_step_1_resume_cover_letter,
    check_for_answer_questions_text,
    apply_step_2_employer_questions, update_seek_profile, review_and_submit)

from job_sites.seek.click_quick_apply_button import click_quick_apply_button
from job_sites.seek.get_job_description import get_job_description
from job_sites.seek.login import login_to_seek
from sqlalchemy import select

if __name__ == "__main__":
    logged_in_driver = login_to_seek()
    if logged_in_driver:
        session = Session(engine)

        not_quick_applies = select(Job).where(Job.is_quick_apply == 0)

        for fail_job in session.scalars(not_quick_applies):
            print(f"➡️Processing job: {fail_job.link}, job_id: {fail_job.provider_id}")
            logged_in_driver.get(fail_job.link)
            logged_in_driver.get(
                f"https://www.seek.com.au/job/{fail_job.provider_id}/apply/"
            )
            click_quick_apply_button(logged_in_driver)
            job_description = get_job_description(logged_in_driver)
            cover_letter = process_cover_letter_openai(job_description)
            success = apply_step_1_resume_cover_letter(logged_in_driver, cover_letter)
            if check_for_answer_questions_text(logged_in_driver):
                print("✅ Step 2 in progress...")
                apply_step_2_employer_questions(logged_in_driver)
                input('check everything ...')

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
        # Close the session
        session.close()
