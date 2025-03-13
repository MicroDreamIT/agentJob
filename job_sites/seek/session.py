import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from core.config import CHROME_DRIVER_PATH  # ✅ Import from config

COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"


def load_seek_session():
    """Loads Seek cookies and keeps the browser session open."""

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
            driver.add_cookie(cookie)  # ✅ Load all cookies properly

        print("✅ Cookies loaded successfully!")

        # Step 3: Refresh to apply cookies
        driver.get("https://www.seek.com.au/profile/me")  # ✅ Check login
        time.sleep(5)

        # Step 4: Check if login was successful
        if "Sign out" in driver.page_source or "My account" in driver.page_source:
            print("✅ Successfully logged in!")
        else:
            print("⚠️ Login failed. Session may have expired.")

        # Step 5: Keep the browser open instead of quitting
        input("🔄 Press Enter to close the browser manually when you're done using it...")

        return driver  # Keep session alive

    except FileNotFoundError:
        print("⚠️ No saved session found. Run login.py first.")
        return None


if __name__ == "__main__":
    driver = load_seek_session()
