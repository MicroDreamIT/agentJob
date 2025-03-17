from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def apply_on_job(driver, job_id):
    original_window = driver.current_window_handle
    wait = WebDriverWait(driver, 15)

    try:
        # 1. Click Job on left-side (precisely)
        job_card_selector = f"article[data-job-id='{job_id}']"
        job_card = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, job_card_selector)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", job_card)
        job_card.click()

        # 2. Wait explicitly for job detail (right side) panel to load fully
        detail_panel = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']"))
        )

        # 3. Click 'Quick apply' button explicitly from right side detail
        quick_apply_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "a[data-automation='job-detail-apply']"))
        )
        quick_apply_btn_text = quick_apply_btn.text.lower()

        if 'quick apply' in quick_apply_btn_text:
            quick_apply_btn.click()
            # 4. Wait explicitly for new tab opening
            wait.until(EC.number_of_windows_to_be(2))

            # Switch to newly opened tab
            new_window = [window for window in driver.window_handles if window != original_window][0]
            driver.switch_to.window(new_window)
            print("✅ Quick apply form opened in new tab.")

            # TODO: Add quick apply form filling logic here

            # After applying, close new tab
            driver.close()

            # Switch back to original window
            driver.switch_to.window(original_window)

            return 'quick_apply'

    except (TimeoutException, NoSuchElementException) as e:
        print(f"⚠️ Quick Apply not found or error occurred: {e}")
        return 'external_apply'
