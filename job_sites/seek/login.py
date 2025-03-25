import time
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from core.config import CHROME_DRIVER_PATH, SEEK_EMAIL
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC

COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"

def scroll_to_element_and_click(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()  # Scroll to the element
    element.click()  # Then click



def login_to_seek(driver):
    """Logs into Seek by navigating from homepage, entering email, and waiting for OTP."""



    # Step 1: Open Seek homepage
    driver.get("https://www.seek.com.au/")

    # Wait for page to load completely
    wait = WebDriverWait(driver, 15)

    # Step 2: Find the "Sign in" button using data-automation attribute
    try:
        sign_in_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[@data-automation='dashboardSignIn']"))
        )

        # Scroll into view before clicking
        driver.execute_script("arguments[0].scrollIntoView();", sign_in_button)
        time.sleep(1)

        # Try normal click
        try:
            sign_in_button.click()
        except:
            # If normal click fails, use JavaScript
            driver.execute_script("arguments[0].click();", sign_in_button)

        print("🔑 Navigated to Seek login page...")
        time.sleep(3)

    except Exception as e:
        print("⚠️ Could not find or click 'Sign in' button:", e)
        driver.quit()
        return

    # Step 3: Enter email
    try:
        email_input = wait.until(EC.presence_of_element_located((By.ID, "emailAddress")))
        email_input.send_keys(SEEK_EMAIL)
        print("✉️ Email entered:", SEEK_EMAIL)
        time.sleep(2)

        # Click "Email me a sign-in code"
        send_code_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-cy='login']")))
        send_code_button.click()
        print("📩 Sent OTP request...")
        time.sleep(5)  # Wait for OTP email

    except Exception as e:
        print("⚠️ Could not enter email:", e)
        driver.quit()
        return

    # User manually enters OTP from email
    otp_code = input("Enter the 6-digit OTP: ").strip()
    assert len(otp_code) == 6, "OTP must be exactly 6 digits."

    # Wait briefly for OTP input field to be ready
    time.sleep(2)

    # Target the hidden single input (correct way)
    otp_input = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="verification input"]')
    otp_input.send_keys(otp_code)

    # Submit the OTP (pressing Enter often works)
    otp_input.send_keys(Keys.RETURN)

    # Wait for login to complete
    time.sleep(5)

    print(f"Logged in page title: {driver.title}")


    # Step 5: Save cookies after successful login
    cookies = driver.get_cookies()
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(cookies, f)

    return driver

