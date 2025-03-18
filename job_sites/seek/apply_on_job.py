from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time

from job_sites.for_ai_process.get_the_job_description import get_the_job_description
from job_sites.for_ai_process.process_cover_letter_openai import process_cover_letter_openai

def extract_job_details(driver, wait):
    try:
        job_details_element = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']"))
        )

        def safe_extract(selector, default="Not specified"):
            try:
                return job_details_element.find_element(By.CSS_SELECTOR, selector).text.strip()
            except NoSuchElementException:
                return default

        job_details_element = driver.find_element(By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']")

        # Extract details
        title = safe_extract(job_details_element, "h1[data-automation='job-detail-title']")
        company = safe_extract(job_details_element, "span[data-automation='advertiser-name']")
        location = safe_extract("span[data-automation='job-detail-location']")
        salary = safe_extract(job_details_element, "span[data-automation='job-detail-salary']")
        description = safe_extract("div[data-automation='jobAdDetails']")

        job_text = (
            f"Job Title: {title}\n"
            f"Company: {company}\n"
            f"Location: {location}\n"
            f"Salary: {salary}\n\n"
            f"Description:\n{description}"
        )

        return job_text

    except TimeoutException as e:
        print(f"⚠️ Error extracting job details: {e}")
        return None

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

        job_text = extract_job_details(driver, job_id)
        print(job_text)  # Debug print, can remove in production

        # Step 2: Explicitly wait for job details panel
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']"))
        )

        # Click the Quick Apply button explicitly via JavaScript
        quick_apply_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[data-automation='job-detail-apply']"))
        )
        if 'quick apply' in quick_apply_button.text.lower():
            driver.execute_script("arguments[0].click();", quick_apply_button)

            # Crucial: Wait longer for the new tab to fully open
            wait.until(EC.number_of_windows_to_be(2))

            # Switch to newly opened tab
            new_tab = [tab for tab in driver.window_handles if tab != original_window][0]
            driver.switch_to.window(new_tab)

            print(f"✅ Quick Apply form opened successfully for job {job_id}.")

            description = get_the_job_description()
            cover_letter = process_cover_letter_openai(description)

            driver.close()
            driver.switch_to.window(original_window)

            return True

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Quick Apply unavailable for job ID {job_id}: {e}")

    return False