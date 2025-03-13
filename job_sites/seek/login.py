from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pickle
import time
from core.config import CHROME_DRIVER_PATH  # ✅ Import from config

COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"


def login_to_seek():
    """Logs into Seek by navigating from homepage, then saves session cookies."""

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

    # Step 1: Open Seek homepage FIRST
    driver.get("https://www.seek.com.au/")
    time.sleep(3)  # Allow page to load

    # Step 2: Find and click the "Sign in" button
    try:
        sign_in_button = driver.find_element(By.LINK_TEXT, "Sign in")
        sign_in_button.click()
        print("🔑 Navigated to Seek login page...")
        time.sleep(3)
    except Exception as e:
        print("⚠️ Could not find Sign in button:", e)
        driver.quit()
        return

    # Step 3: Wait for manual login
    input("🔑 Log in manually, then press Enter...")

    # Step 4: Save cookies after successful login
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(cookies, f)

    print("✅ Seek login session saved!")
    driver.quit()


if __name__ == "__main__":
    login_to_seek()
