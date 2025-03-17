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
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']")))

        # Step 2: Find and explicitly click Quick Apply using JavaScript to ensure event triggers
        quick_apply_button = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-automation='job-detail-apply']")))

        if 'quick apply' in quick_apply_button.text.lower():
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", quick_apply_button)
            driver.execute_script("arguments[0].click();", quick_apply_button)

            # Explicitly wait for new tab to open
            wait.until(EC.number_of_windows_to_be(20))

            # Switch explicitly to new tab
            new_tab = [tab for tab in driver.window_handles if tab != driver.current_window_handle][0]
            driver.switch_to.window(new_tab)

            print("✅ Quick Apply form opened successfully.")

            # TODO: Form filling logic here

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            return True

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Quick Apply unavailable for job ID {job_id}: {e}")

    return False