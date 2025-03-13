import pickle
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from core.config import CHROME_DRIVER_PATH  # ✅ Import from config

COOKIE_FILE = "seek_cookies.pkl"

def load_seek_session():
    """Opens a new tab, loads cookies, and restores Seek session."""

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # Step 1: Open Seek homepage
    driver.get("https://www.seek.com.au/")
    time.sleep(3)

    # Step 2: Load and apply saved cookies
    try:
        with open(COOKIE_FILE, "rb") as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            driver.add_cookie(cookie)  # ✅ Apply all stored cookies

        print("✅ Cookies loaded successfully!")

        # Step 3: Open a new tab and verify login
        driver.execute_script("window.open('https://www.seek.com.au/profile/me', '_blank');")
        print("🔄 Opened new tab for profile page...")
        time.sleep(5)

        # Step 4: Check if login was successful
        driver.switch_to.window(driver.window_handles[1])  # Switch to new tab
        if "Sign out" in driver.page_source or "My account" in driver.page_source:
            print("✅ Successfully logged in!")
        else:
            print("⚠️ Login failed. Session may have expired.")

    except FileNotFoundError:
        print("⚠️ No saved session found. Run login.py first.")

    input("🔄 Press Enter to close the browser...")
    driver.quit()

if __name__ == "__main__":
    load_seek_session()
