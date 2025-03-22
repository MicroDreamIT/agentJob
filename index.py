job_sites = {
    1: 'seek',
    2: 'indeed'
}
# get input
from selenium import webdriver
from job_sites.seek.login import login_to_seek
from job_sites.seek.search_jobs import search_jobs

if __name__ == "__main__":
    driver = webdriver.Chrome()  # Ensure ChromeDriver is in your PATH or specify the path to the driver
    try:
        logged_in_driver = login_to_seek()
        if logged_in_driver:
            search_jobs(logged_in_driver, what="web-developer-jobs", days=3)
    finally:
        driver.quit()