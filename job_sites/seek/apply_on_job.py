import os
import time
import openai
from difflib import get_close_matches
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from job_sites.for_ai_process.process_cover_letter_openai import process_cover_letter_openai
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException


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
    cover_letter=''
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
            return [False, cover_letter]

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

            new_tab = None
            for tab in driver.window_handles:
                if tab != original_window:
                    new_tab = tab
                    break
            if new_tab:
                driver.switch_to.window(new_tab)
                print("🔄 Switched to new job application tab.")
                try:
                    # Apply Step 1: Resume & Cover Letter
                    success = apply_step_1_resume_cover_letter(driver, cover_letter)
                    if success:
                        print("✅ Step 1 completed successfully!")
                    else:
                        print("⚠️ Step 1 failed! Check logs for errors.")

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

    return [False, cover_letter]


def apply_step_1_resume_cover_letter(driver, cover_letter_text):
    """
    Automates Step 1 of the job application process:
    - Selects the correct resume
    - Checks "Write a Cover Letter"
    - Pastes the cover letter
    - Clicks the "Continue" button
    """

    wait = WebDriverWait(driver, 15)

    try:
        # ✅ Step 1: Select Resume from Dropdown
        print("📄 Selecting resume...")

        resume_dropdown = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "select[data-testid='select-input']"))
        )
        resume_dropdown.click()
        time.sleep(2)  # Wait to ensure dropdown expands

        # Debugging: Print all options available
        all_options = driver.find_elements(By.TAG_NAME, "option")
        available_resumes = [opt.text for opt in all_options]
        print(f"📝 Available resumes: {available_resumes}")

        # Ensure the correct resume text exists
        resume_text = "18/3/25 - Resume-sample.pdf"
        if resume_text not in available_resumes:
            print(f"⚠️ Resume '{resume_text}' not found! Check dropdown options.")
            return False

        resume_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, f"//option[contains(text(), '{resume_text}')]"))
        )
        resume_option.click()

        print("✅ Resume selected!")

        # ✅ Step 2: Select "Write a Cover Letter"
        print("📝 Selecting 'Write a Cover Letter' option...")

        cover_letter_radio = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='coverLetter-method-change']"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", cover_letter_radio)
        time.sleep(1)  # Wait to ensure visibility
        driver.execute_script("arguments[0].click();", cover_letter_radio)

        print("✅ 'Write a Cover Letter' selected!")

        # ✅ Step 3: Paste the Cover Letter
        print("✍️ Pasting cover letter...")

        cover_letter_textarea = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[data-testid='coverLetterTextInput']"))
        )
        cover_letter_textarea.clear()
        cover_letter_textarea.send_keys(cover_letter_text)

        print("✅ Cover letter pasted!")

        # ✅ Step 4: Click "Continue"
        print("🚀 Clicking 'Continue' button...")

        continue_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='continue-button']"))
        )

        driver.execute_script("arguments[0].scrollIntoView();", continue_button)
        time.sleep(1)  # Ensure smooth scrolling before clicking
        driver.execute_script("arguments[0].click();", continue_button)

        print("✅ Continue button clicked! Moving to next step...")

        return True

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"⚠️ Error in Step 1 (Resume & Cover Letter Selection): {e}")
        print("🔎 Debug: Printing page source for troubleshooting...")
        print(driver.page_source)  # Check for missing elements in the page
        return False


def apply_step_2_employer_questions(driver, cv_text):
    """
    Automates Step 2 of the job application process:
    - Detects all employer questions dynamically
    - Uses OpenAI to generate responses based on CV
    - Fills in answers in the correct fields
    - Clicks "Continue" to submit answers

    Parameters:
        driver (WebDriver): Selenium WebDriver instance.
        cv_text (str): Extracted text from the CV.
    """

    wait = WebDriverWait(driver, 15)

    try:
        print("🔍 Detecting employer questions...")
        questions = driver.find_elements(By.CSS_SELECTOR, "label")  # General way to find questions

        if not questions:
            print("⚠️ No employer questions found. Skipping Step 2.")
            return True

        for index, question_label in enumerate(questions):
            question_text = question_label.text.strip()

            if not question_text:
                continue  # Skip empty labels

            print(f"📝 Processing Question {index+1}: {question_text}")

            # **Step 1: Identify the Input Type**
            input_field = None
            input_type = None

            # Try finding input fields (text, radio, checkbox, select)
            try:
                input_field = question_label.find_element(By.XPATH, "following-sibling::input")
                input_type = "text"
            except:
                try:
                    input_field = question_label.find_element(By.XPATH, "following-sibling::textarea")
                    input_type = "textarea"
                except:
                    try:
                        input_field = question_label.find_element(By.XPATH, "following-sibling::select")
                        input_type = "dropdown"
                    except:
                        try:
                            input_field = question_label.find_element(By.XPATH, "following-sibling::div//input[@type='radio']")
                            input_type = "radio"
                        except:
                            try:
                                input_field = question_label.find_element(By.XPATH, "following-sibling::div//input[@type='checkbox']")
                                input_type = "checkbox"
                            except:
                                print(f"⚠️ No matching input found for: {question_text}")
                                continue

            print(f"🔍 Detected input type: {input_type}")

            # **Step 2: Get Answer from OpenAI**
            openai_response = get_openai_answer(question_text, cv_text)
            print(f"🤖 AI Answer: {openai_response}")

            # **Step 3: Fill in the Answer Correctly**
            if input_type in ["text", "textarea"]:
                input_field.clear()
                input_field.send_keys(openai_response)

            elif input_type == "dropdown":
                select = Select(input_field)
                best_option = find_best_dropdown_option(select.options, openai_response)
                select.select_by_visible_text(best_option)

            elif input_type == "radio":
                select_best_radio_option(driver, question_label, openai_response)

            elif input_type == "checkbox":
                if "yes" in openai_response.lower():
                    driver.execute_script("arguments[0].click();", input_field)  # Click checkbox

        # **Step 4: Click "Continue"**
        print("🚀 Clicking 'Continue' button...")
        continue_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='continue-button']")))
        driver.execute_script("arguments[0].click();", continue_button)

        print("✅ Employer Questions Completed!")
        return True

    except Exception as e:
        print(f"⚠️ Error in Step 2 (Employer Questions): {e}")
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


def find_best_dropdown_option(options, ai_answer):
    """
    Finds the best matching option in a dropdown.

    Parameters:
        options (list): List of dropdown options.
        ai_answer (str): AI-generated answer.

    Returns:
        str: The closest matching option.
    """
    option_texts = [opt.text for opt in options]
    best_match = get_close_matches(ai_answer, option_texts, n=1, cutoff=0.6)
    return best_match[0] if best_match else option_texts[0]


def select_best_radio_option(driver, question_label, ai_answer):
    """
    Selects the best radio button based on the AI answer.

    Parameters:
        driver (WebDriver): Selenium WebDriver instance.
        question_label (WebElement): The label element of the question.
        ai_answer (str): AI-generated answer.
    """
    radio_buttons = question_label.find_elements(By.XPATH, "following-sibling::div//input[@type='radio']")

    for radio in radio_buttons:
        label = radio.find_element(By.XPATH, "following-sibling::label").text.strip()
        if ai_answer.lower() in label.lower():
            driver.execute_script("arguments[0].click();", radio)
            return