import os

import openai
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
from job_sites.for_ai_process.process_cover_letter_openai import process_cover_letter_openai
from selenium.webdriver.support.ui import WebDriverWait, Select

client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
PREDEFINED_ANSWERS = {
    "Which of the following statements best describes your right to work in Australia?":
        "I require sponsorship to work for a new employer (e.g. 482, 457)",
    "What's your expected annual base salary?": "$90k"
}

def extract_job_details(driver):
    """Extract job details (Title, Company, Location, Salary, Description) in text format."""
    try:
        job_details_element = driver.find_element(By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']")
        job_text = job_details_element.text.strip()
        return job_text
    except NoSuchElementException:
        print("⚠️ Job details not found.")
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
        time.sleep(5)

        job_text = extract_job_details(driver)
        cover_letter = process_cover_letter_openai(job_text)
        print(cover_letter)  # Debug print, can remove in production

        if job_text is None:
            return False

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
            time.sleep(5)

            # Switch to newly opened tab
            new_tab = [tab for tab in driver.window_handles if tab != original_window][0]
            driver.switch_to.window(new_tab)

            try:
                apply_form = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "form"))
                )

                apply_step_1_resume_cover_letter(driver, cover_letter)
                apply_step_2_employer_questions(driver)

                print(f"✅ Quick Apply form loaded successfully for job {job_id}.")



            except TimeoutException:
                print(f"⚠️ Quick Apply form not detected for job {job_id}.")
                driver.close()
                driver.switch_to.window(original_window)
                return [False, cover_letter]

            # ✅ **Fix: Give extra time before interacting with form**
            time.sleep(3)

            print("🚀 Ready to fill the application form...")

            # Further automation: Filling inputs etc. (not implemented here)

            # Closing tab only after proper processing
            driver.close()
            driver.switch_to.window(original_window)

            return [True, cover_letter]

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Quick Apply unavailable for job ID {job_id}: {e}")

    return False


def apply_step_1_resume_cover_letter(driver, cover_letter_text):
    """
    Automates Step 1 of the job application process:
    - Selects the correct resume
    - Checks "Write a Cover Letter"
    - Pastes the cover letter
    - Clicks the "Continue" button

    Parameters:
        driver (WebDriver): Selenium WebDriver instance.
        cover_letter_text (str): AI-generated cover letter.
    """

    wait = WebDriverWait(driver, 15)

    try:
        # ✅ Step 1: Select Resume from Dropdown
        print("📄 Selecting resume...")

        resume_dropdown = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[data-testid='select-input']")))
        resume_dropdown.click()

        resume_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//option[contains(text(), '14/3/25 - ShahanurSharifGMCv.pdf')]")))
        resume_option.click()

        print("✅ Resume selected!")

        # ✅ Step 2: Select "Write a Cover Letter"
        print("📝 Selecting 'Write a Cover Letter' option...")

        cover_letter_radio = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-testid='coverLetter-method-change']")))
        driver.execute_script("arguments[0].click();", cover_letter_radio)

        print("✅ 'Write a Cover Letter' selected!")

        # ✅ Step 3: Paste the Cover Letter
        print("✍️ Pasting cover letter...")

        cover_letter_textarea = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-testid='coverLetterTextInput']")))
        cover_letter_textarea.clear()
        cover_letter_textarea.send_keys(cover_letter_text)

        print("✅ Cover letter pasted!")

        # ✅ Step 4: Click "Continue"
        print("🚀 Clicking 'Continue' button...")

        continue_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='continue-button']")))
        driver.execute_script("arguments[0].click();", continue_button)

        print("✅ Continue button clicked! Moving to next step...")

        return True

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Error in Step 1 (Resume & Cover Letter Selection): {e}")
        return False


def get_openai_answer(question, choices, cv_text):
    """
    Generates an answer for a given job application question using OpenAI.

    Parameters:
        question (str): The employer question.
        choices (list): Possible choices (for radio, select, checkbox).
        cv_text (str): The CV text to reference.

    Returns:
        str: The best-matching answer.
    """

    prompt = f"""
    Based on my CV:

    {cv_text}

    Please provide a concise answer to the following employer question in a job application:

    {question}

    Choices: {', '.join(choices) if choices else 'N/A'}

    Keep it professional and relevant. If multiple options apply, return a list of choices.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an HR assistant helping to answer job application questions."},
                {"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ OpenAI API Error: {e}")
        return "N/A"


def apply_step_2_employer_questions(driver):
    cv_text = os.getenv("CV_TEXT")
    """
    Automates Step 2 of the job application process:
    - Detects if the "Answer Employer Questions" step exists
    - Dynamically fills out different form types (input, select, checkbox, radio, textarea)
    - Uses OpenAI to answer technical questions based on CV
    - Clicks "Continue" to proceed

    Parameters:
        driver (WebDriver): Selenium WebDriver instance.
        cv_text (str): The text extracted from the user's CV.
        keep in mind those predefined answers:
        
        predefined question answer:
        Which of the following statements best describes your right to work in Australia?
        dropdown -> I require sponsorship to work for a new employer (e.g. 482, 457)
        
        What's your expected annual base salary?
        90k
    """
    wait = WebDriverWait(driver, 15)

    try:
        # ✅ Step 1: Check if employer questions exist
        print("🔍 Checking for employer questions...")
        try:
            employer_questions_section = wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            print("✅ Employer questions found!")
        except TimeoutException:
            print("⚠️ No employer questions found. Skipping Step 2.")
            return True

        # ✅ Step 2: Find all question containers dynamically
        question_containers = driver.find_elements(By.TAG_NAME, "label")

        for question_label in question_containers:
            try:
                # Extract question text
                question_text = question_label.text.strip()
                if not question_text:
                    continue

                # Predefined answer check
                answer = PREDEFINED_ANSWERS.get(question_text)

                # If no predefined answer, use OpenAI
                if not answer:
                    answer = get_openai_answer(question_text, [], cv_text)

                print(f"📝 Answering: {question_text} -> {answer}")

                # ✅ Handle Input Fields (text, number, email)
                try:
                    input_field = question_label.find_element(By.XPATH, "following-sibling::input")
                    input_type = input_field.get_attribute("type")

                    if input_type in ["text", "number", "email"]:
                        input_field.clear()
                        input_field.send_keys(answer)
                        print("✅ Answered using Input Field.")
                        continue
                except NoSuchElementException:
                    pass

                # ✅ Handle Textarea
                try:
                    textarea = question_label.find_element(By.XPATH, "following-sibling::textarea")
                    textarea.clear()
                    textarea.send_keys(answer)
                    print("✅ Answered using Textarea.")
                    continue
                except NoSuchElementException:
                    pass

                # ✅ Handle Dropdown (Select)
                try:
                    select_element = question_label.find_element(By.XPATH, "following-sibling::select")
                    select = Select(select_element)
                    select.select_by_visible_text(answer)
                    print("✅ Answered using Dropdown.")
                    continue
                except NoSuchElementException:
                    pass

                # ✅ Handle Radio Buttons
                try:
                    radio_buttons = question_label.find_elements(By.XPATH, "following-sibling::input[@type='radio']")
                    for btn in radio_buttons:
                        if btn.get_attribute("value") == answer:
                            driver.execute_script("arguments[0].click();", btn)
                            print("✅ Answered using Radio Button.")
                            break
                    continue
                except NoSuchElementException:
                    pass

                # ✅ Handle Checkboxes
                try:
                    checkboxes = question_label.find_elements(By.XPATH, "following-sibling::input[@type='checkbox']")
                    for box in checkboxes:
                        if box.get_attribute("value") in answer:
                            driver.execute_script("arguments[0].click();", box)
                            print("✅ Answered using Checkbox.")
                    continue
                except NoSuchElementException:
                    pass

                print("⚠️ No suitable input method found for this question.")

            except NoSuchElementException:
                print("⚠️ Skipping an unrecognized question format.")

        # ✅ Step 3: Click "Continue"
        print("🚀 Clicking 'Continue' button to proceed...")
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue')]")))
        driver.execute_script("arguments[0].click();", continue_button)
        print("✅ Step 2 Completed. Moving to next step...")

        return True

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Error in Step 2 (Employer Questions): {e}")
        return False
