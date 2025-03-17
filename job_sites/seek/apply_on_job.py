from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def apply_on_job(driver, job_link):
    original_window = driver.current_window_handle
    driver.get(job_link)

    wait = WebDriverWait(driver, 10)

    try:
        quick_apply_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-automation, 'quickApplyButton')]"))
        )

        quick_apply_btn_text = quick_apply_btn.text.lower()
        if 'quick apply' in quick_apply_btn_text:
            quick_apply_btn.click()

            # Wait for new tab to open
            wait.until(EC.number_of_windows_to_be(2))

            # Switch to new tab
            new_window = [window for window in driver.window_handles if window != original_window][0]
            driver.switch_to.window(new_window)

            print("Quick apply page opened in a new tab.")

            # Continue with your quick apply logic here
            # Example: fill inputs, upload CV, etc.

            # After finishing, close quick apply tab
            driver.close()

            # Switch back to the original tab
            driver.switch_to.window(original_window)

            return 'quick_apply'

    except (TimeoutException, NoSuchElementException):
        print("Quick Apply button not found; external application required.")
        return 'external_apply'
