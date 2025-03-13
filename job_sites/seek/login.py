from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import pickle
import os

from job_sites.core.config import CHROME_DRIVER_PATH

# Cookie file location
COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"


def login_to_seek():
    """Manually log in and save session cookies."""

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # Open Seek login page
    driver.get("https://www.seek.com.au/")

    # Wait for manual login
    input("🔑 Log in manually, then press Enter...")

    # Ensure directory exists
    os.makedirs("job_sites/seek", exist_ok=True)

    # Save cookies
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(driver.get_cookies(), f)

    print(f"✅ Seek login session saved at {COOKIE_FILE}!")
    driver.quit()


if __name__ == "__main__":
    login_to_seek()
