import time

import pyautogui

from core.config import CHROME_DRIVER_PATH
from job_sites.helpers.minimize_chrome import minimize_chrome

job_sites = {
    1: 'seek',
    2: 'indeed'
}
# get input
from selenium import webdriver
from job_sites.seek.login import login_to_seek
from job_sites.seek.search_jobs import search_jobs
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

if __name__ == "__main__":
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    logged_in_driver = login_to_seek(driver)
    whats = [
        # 'full-stack-developer',
        # 'vuejs',
        # 'software-developer',
        # 'python',
        # 'django',
        # 'laravel',
        # 'web-developer',
        'software-engineer',
        # 'front-end-developer',
        # 'back-end-developer',
        # 'reactjs',
        # 'devops',
        # 'aws',
        # 'ibm',
        # 'it-support',
        # 'it-administrator',
        # 'it-manager',
        # 'it-consultant',
        # 'data-analyst',
    ]
    minimize_chrome()
    if logged_in_driver:
        for what in whats:

            # logged_in_driver.minimize_window()
            search_jobs(logged_in_driver, what=what, days=3)
            minimize_chrome()
    driver.quit()