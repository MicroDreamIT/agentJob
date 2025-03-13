import pickle
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time

from job_sites.core.config import CHROME_DRIVER_PATH

# Path to ChromeDriver (Update for your OS)
chrome_driver_path = CHROME_DRIVER_PATH
COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"

def load_seek_session():
    """Loads Seek cookies and opens the session in Selenium."""

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # First, open Seek's homepage
    driver.get("https://www.seek.com.au")

    # Load saved cookies
    try:
        with open(COOKIE_FILE, "rb") as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            if "seek.com.au" in cookie["domain"]:  # ✅ Only add valid Seek cookies
                driver.add_cookie(cookie)

        print("✅ Cookies loaded successfully!")

        # Refresh the page to apply cookies
        driver.refresh()
        time.sleep(5)

        return driver

    except FileNotFoundError:
        print("⚠️ No saved session found. Please run login.py first.")
        return None

if __name__ == "__main__":
    driver = load_seek_session()
    if driver:
        input("Press Enter to close browser...")
        driver.quit()
