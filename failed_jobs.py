# get input
from selenium import webdriver
from sqlalchemy.orm import sessionmaker, Session

from core.database import Job, engine
from job_sites.seek.login import login_to_seek
from job_sites.seek.search_jobs import search_jobs
from sqlalchemy import select

if __name__ == "__main__":


    # Perform the query

    driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH or specify the path to the driver
    try:
        logged_in_driver = login_to_seek()
        if logged_in_driver:
            session = Session(engine)

            failed_jobs = select(Job).where(Job.is_quick_apply == 0)

            for failed_job in session.scalars(failed_jobs):
                print(failed_job)

            # Close the session
            session.close()
    finally:
        driver.quit()