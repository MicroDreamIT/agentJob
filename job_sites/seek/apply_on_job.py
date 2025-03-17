from selenium.common import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


def apply_on_job(driver, job_link):
    driver.execute_script(f"window.open('{job_link}');")
    driver.switch_to.window(driver.window_handles[-1])

    try:
        wait = WebDriverWait(driver, 10)
        quick_apply_btn = wait.until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@data-automation, 'quickApplyButton')]"))
        )
        quick_apply_btn.click()
        print("Quick apply button clicked.")
        # Proceed with quick apply logic...
        quick_apply_found = True

    except (TimeoutException, NoSuchElementException):
        print("No Quick Apply available.")
        quick_apply_btn = None
        quick_apply_found = False
    finally:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    return 'quick_apply' if quick_apply_found else 'external_apply'
