from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pickle

from job_sites.core.config import CHROME_DRIVER_PATH



def login_to_seek():
    """Logs into Seek and saves session cookies using Selenium."""

    # Use Service() to initialize ChromeDriver correctly
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)  # ✅ Fixed

    # Open Seek login page
    driver.get("https://www.seek.com.au/sign-in")

    # Wait for manual login
    input("🔑 Log in manually, then press Enter...")

    # Save session cookies
    cookies = driver.get_cookies()
    with open("job_sites/seek/seek_cookies.pkl", "wb") as f:
        pickle.dump(cookies, f)

    print("✅ Seek login session saved!")
    driver.quit()


if __name__ == "__main__":
    login_to_seek()
