import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from core.config import CHROME_DRIVER_PATH  # ✅ Import from config

COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"

def load_seek_session():
    """Loads Seek cookies and verifies if the session is still active."""

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # Step 1: Open Seek homepage first
    driver.get("https://www.seek.com.au/")
    time.sleep(3)

    # Step 2: Load and apply saved cookies
    try:
        with open(COOKIE_FILE, "rb") as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            if "seek.com.au" in cookie["domain"]:  # ✅ Apply only Seek cookies
                driver.add_cookie(cookie)

        print("✅ Cookies loaded successfully!")

        # Step 3: Navigate to profile page to verify login
        driver.get("https://www.seek.com.au/profile/me")
        time.sleep(5)

        # Step 4: Check if login was successful
        if "Sign out" in driver.page_source or "My account" in driver.page_source:
            print("✅ Successfully logged in!")
        else:
            print("⚠️ Login failed. Session may have expired.")

        return driver

    except FileNotFoundError:
        print("⚠️ No saved session found. Run login.py first.")
        return None

if __name__ == "__main__":
    driver = load_seek_session()
    if driver:
        input("Press Enter to close browser...")
        driver.quit()
