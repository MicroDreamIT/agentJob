from datetime import datetime
from sqlite3 import IntegrityError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time
from core.config import CHROME_DRIVER_PATH, SEEK_EMAIL
from core.database import create_connection, Job, close_connection
from selenium.common.exceptions import NoSuchElementException, TimeoutException

COOKIE_FILE = "job_sites/seek/seek_cookies.pkl"

def scroll_to_element_and_click(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()  # Scroll to the element
    element.click()  # Then click


def open_job():
    # before click check database matches job id
    # if doesnt match, open link in a new tab
    #if matches, then click the next job
    #
    # store job id, link, job site in database
    # click 'quick apply'
    # call apply_on_job
    pass

def apply_on_job():
    # send job description and CV to openAI to generate cover letter
    # get the cover letter
    #click continue
    # dynamically get the input and questions, to openAI to generate answers
    #fill the inputs
    # answer 'Which of the following statements best describes your right to work in Australia?' select -> I require sponsorship to work for a new employer (e.g. 482, 457)
    #click 'continue'
    # click submit application
    # close the tab
    # goto job board tab
    # call open_job()
    pass



def login_to_seek():
    """Logs into Seek by navigating from homepage, entering email, and waiting for OTP."""

    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service)

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

    # Step 4: Wait for user to manually enter OTP
    input("🔑 Enter OTP manually in the browser, then press Enter here...")

    # Step 5: Save cookies after successful login
    cookies = driver.get_cookies()
    print("📝 Saved Cookies:", cookies)
    with open(COOKIE_FILE, "wb") as f:
        pickle.dump(cookies, f)
    
    
    return driver

