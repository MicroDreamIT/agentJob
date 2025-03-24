from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

def get_job_description(driver):
    click_view_job_description(driver)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id='jobDescription-close']"))
    )
    try:
        # Wait for the job description modal to be visible
        job_details_element = driver.find_element(By.CSS_SELECTOR, "div[id='jobDescription']")
        job_text = job_details_element.text.strip()
        click_to_close_job_description(driver)
        print(f"✅ Extracted job description: {job_text}")
        return job_text

    except Exception as e:
        print(f"Failed to extract job description: {str(e)}")
        return None

def click_to_close_job_description(driver):
    close_button = driver.find_element(By.ID, "jobDescription-close")
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(close_button))

    # Optional: Ensure the button is in view
    ActionChains(driver).move_to_element(close_button).perform()

    # Click the button to close the modal
    close_button.click()


def click_view_job_description(driver):
    try:
        # Wait until the text is visible and the element is clickable
        button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='View job description']"))
        )

        # Use ActionChains to ensure visibility and reach if needed
        ActionChains(driver).move_to_element(button).perform()

        # Click the button
        button.click()
        print("✅ Clicked 'View job description'")


    except Exception as e:
        print(f"Failed to click 'View job description': {str(e)}")
        return False

    return True