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
    logged_in_driver = login_to_seek()
    whats = [
        'full-stack-developer-jobs',
        # 'data-analyst-jobs',
        # 'vuejs-jobs',
        # 'reactjs-jobs',
        # 'python-jobs',
        # 'laravel-jobs',
        # 'django-jobs',
        # 'software-engineer-jobs',
        # 'devops-jobs',
        # 'aws-jobs',
        # 'ibm-jobs',
        # 'it-support-jobs',
        # 'it-administrator-jobs',
        # 'it-manager-jobs',
        # 'it-consultant-jobs',
        # 'software-developer-jobs',
        # 'web-developer-jobs',
        # 'front-end-developer-jobs',
        # 'back-end-developer-jobs',
    ]
    if logged_in_driver:
        for what in whats:
            # logged_in_driver.minimize_window()
            search_jobs(logged_in_driver, what=what, days=3)
    driver.quit()