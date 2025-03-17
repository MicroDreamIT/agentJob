from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time

def apply_on_job(driver, job_id):
    original_window = driver.current_window_handle
    wait = WebDriverWait(driver, 15)

    try:
        # Step 1: Precisely click the job title in the left-side panel
        job_title_selector = f"article[data-job-id='{job_id}'] a[data-automation='jobTitle']"
        job_title_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, job_title_selector)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_title_link)
        driver.execute_script("arguments[0].click();", job_title_link)

        # Wait briefly to ensure DOM updates
        time.sleep(2)

        # Step 2: Explicitly wait for job details panel
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']"))
        )

        # Step 3: Explicitly wait for "Quick Apply" button
        quick_apply_button = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "a[data-automation='job-detail-apply']"
        )))

        if 'quick apply' in quick_apply_button.text.lower():
            quick_apply_button.click()

            # Wait explicitly for the new tab to open
            wait.until(EC.number_of_windows_to_be(2))

            # Switch clearly to the newly opened tab
            new_tab = [tab for tab in driver.window_handles if tab != original_window][0]
            driver.switch_to.window(new_tab)
            print("✅ Quick Apply form opened successfully.")

            # TODO: add your form filling logic here

            # Close the application tab after applying
            driver.close()

            # Switch back to original window
            driver.switch_to.window(original_window)

            return True  # This return is now correctly placed

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Quick Apply unavailable for job ID {job_id}: {e}")

    return False  # This ensures function always returns a boolean
