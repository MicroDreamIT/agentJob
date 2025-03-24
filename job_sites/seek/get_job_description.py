from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def get_job_description(driver, timeout=15):
    if not click_view_job_description(driver):
        print("⚠️ Unable to click 'View job description'")
        return None

    try:
        # Wait explicitly for the modal containing the description to be visible
        WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.ID, "jobDescription"))
        )

        job_details_element = driver.find_element(By.ID, "jobDescription")
        job_text = job_details_element.text.strip()
        print("✅ Successfully extracted job description.")

        click_to_close_job_description(driver)

        return job_text

    except TimeoutException:
        print("⚠️ Timeout: Job description modal did not appear.")
        return None
    except Exception as e:
        print(f"⚠️ Unexpected error while extracting job description: {e}")
        return None

def click_view_job_description(driver):
    try:
        button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='View job description']"))
        )
        ActionChains(driver).move_to_element(button).click().perform()
        print("✅ Clicked 'View job description'")
        return True
    except TimeoutException:
        print("⚠️ Timeout: 'View job description' button not clickable.")
        return False
    except Exception as e:
        print(f"⚠️ Failed to click 'View job description': {e}")
        return False

def click_to_close_job_description(driver):
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "jobDescription-close"))
        )
        ActionChains(driver).move_to_element(close_button).click().perform()
        print("✅ Closed job description modal.")
        return True
    except Exception as e:
        print(f"⚠️ Failed to close job description modal: {e}")
        return False