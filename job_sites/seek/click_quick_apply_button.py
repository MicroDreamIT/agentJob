from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def click_quick_apply_button(driver):
    try:
        # Wait until the text is visible and the element is clickable
        button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Quick apply']"))
        )

        # Use ActionChains to ensure visibility and reach if needed
        ActionChains(driver).move_to_element(button).perform()

        # Click the button
        button.click()
        print("✅ Clicked 'Quick apply'")

    except Exception as e:
        print(f"Failed to click 'Quick apply': {str(e)}")
        return False

    return True