from selenium.common import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def apply_on_job(driver, job_id):
    original_window = driver.current_window_handle
    wait = WebDriverWait(driver, 15)

    try:
        # 1. Click the job listing explicitly with JS
        job_card_selector = f"article[data-job-id='{job_id}']"
        job_card = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, job_card_selector)))

        # Scroll precisely to the element and reliably click via JavaScript
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        driver.execute_script("arguments[0].click();", job_card)

        # 2. Wait explicitly for job detail panel to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']")))

        # 2. Find the Quick Apply button
        quick_apply_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[data-automation='job-detail-apply']")))

        if 'quick apply' in quick_apply_button.text.lower():
            quick_apply_button.click()

            # Wait explicitly for new tab to open
            wait.until(EC.number_of_windows_to_be(2))

            # Switch to new tab
            new_window = [w for w in driver.window_handles if w != driver.current_window_handle][0]
            driver.switch_to.window(new_window)

            print("✅ Quick Apply form opened.")

            # TODO: Continue form filling

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

            return True

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Error applying: {e}")
        return False
