from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pickle
import os
import time

from job_sites.core.config import CHROME_DRIVER_PATH

# Path to ChromeDriver
chrome_driver_path = "/usr/local/bin/chromedriver"

# Cookie file location
COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"


def load_seek_session():
    """Loads Seek session with saved cookies."""

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # Open Seek
    driver.get("https://www.seek.com.au/")

    # Check if cookie file exists
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, "rb") as f:
            cookies = pickle.load(f)

        # Add cookies to browser
        for cookie in cookies:
            driver.add_cookie(cookie)

        print("✅ Session restored! Refreshing page...")
        driver.refresh()  # Reload page with cookies applied

        time.sleep(5)  # Give time to verify if logged in

        if "Sign out" in driver.page_source:
            print("✅ You are still logged in!")
        else:
            print("⚠️ Session might have expired, please log in again.")

    else:
        print("⚠️ No saved session found. Run login.py first.")

    driver.quit()


if __name__ == "__main__":
    load_seek_session()
