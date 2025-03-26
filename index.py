import time

import pyautogui

from core.config import CHROME_DRIVER_PATH

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

def minimize_chrome():
    # Command + M is the shortcut to minimize a window in macOS
    pyautogui.hotkey('command', 'm')
    print('minimize did not worked')
    time.sleep(1)  # Wait a bit to ensure the command is processed

if __name__ == "__main__":
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    logged_in_driver = login_to_seek(driver)
    whats = [
        # 'full-stack-developer',
        # 'vuejs',
        # 'software-developer',
        'python',
        # 'django',
        # 'laravel',
        # 'software-engineer',
        # 'web-developer',
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