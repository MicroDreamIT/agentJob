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
CV_TEXT = os.getenv("CV_TEXT")

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

                    automate_employer_questions(driver)
                    # apply_step_2_employer_questions(driver)

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


import re
from selenium.webdriver.support.ui import Select

def apply_step_2_employer_questions(driver, cv_text):
    """
    Automates Step 2 of the job application process:
    - Skips pre-filled answers
    - Uses pre-defined answers for known questions
    - Uses OpenAI only for unknown questions
    - Handles checkboxes dynamically
    - Matches integer responses correctly
    """
    predefined_answers = {
        "How many years' experience do you have as a full stack developer?": {
            "dropdown": "More than 5 years", "text": "13 Years"},
        "How many years' experience do you have as a Ruby on Rails Developer?": {"dropdown": "0-1 years",
                                                                                 "text": "1 Year"},
        "Which of the following statements best describes your right to work in Australia?": "Skip",
        "Do you have a current Australian driver's licence?": "No",
        "Do you own or have regular access to a car?": "Yes",
        "How many years' experience do you have as a ServiceNow Developer?": "No experience",
        "Do you hold Australian Security Clearance?": "No",
        "How much notice are you required to give your current employer?": "1 week",
        "How many years' experience do you have as a C++ Developer?": "2",
        "How many years' experience do you have as a Java Software Engineer?": "1",
        "Have you worked in a role which requires CSS development experience?": "Yes",
        "How many years' experience do you have as a software engineer?": "5",
        "How many years' experience do you have in a DevOps role?": "1",
        "How many years' experience do you have as an ASP.Net MVC Developer?": "No experience",
        "What city are you based in?": "Perth",
        "Are you an Australian/NZ citizen?": "No",
        "What are your salary expectations?": "$100k",
        "Do you have full working rights in Australia?": "No",
        "Will you require visa sponsorship either now or in the future?": "Yes",
        "How many years of experience do you possess in a Software Developer or equivalent role?": "instruction: select the last one",
        "Would you be interested in the Fixed Term Position (contract until 31 Dec 2025)?": "Yes",
        "Do you have experience in programming languages C#/.Net or React?": "Yes",
        "What are your salary expectations for the role?": "$100k",
        "How many years' experience do you have as a Full Stack Software Engineer?": {
            "dropdown": "More than 5 years", "text": "13 Years"},
        "How many years' experience do you have working in an agile environment?": {
            "dropdown": "More than 5 years", "text": "13 Years"},
    }
    """
    Automates Step 2 of the job application process:
    - Uses predefined answers when available.
    - Handles text, dropdown, checkboxes, and radio buttons dynamically.
    - Uses OpenAI only when necessary.
    - Skips pre-filled fields.
    """

    wait = WebDriverWait(driver, 15)

    try:
        print("🔍 Detecting employer questions...")

        question_elements = driver.find_elements(By.CSS_SELECTOR, "label")

        if not question_elements:
            print("⚠️ No employer questions found. Skipping Step 2.")
            return True

        for index, question_label in enumerate(question_elements):
            try:
                question_text = question_label.text.strip()

                if not question_text:
                    continue  # Skip empty labels

                print(f"📝 Processing Question {index + 1}: {question_text}")

                # **Step 1: Find Input Field Dynamically**
                input_field = None
                input_type = None

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
                                input_field = question_label.find_element(By.XPATH,
                                                                          "following-sibling::div//input[@type='radio']")
                                input_type = "radio"
                            except:
                                try:
                                    input_field = question_label.find_element(By.XPATH,
                                                                              "following-sibling::div//input[@type='checkbox']")
                                    input_type = "checkbox"
                                except:
                                    print(f"⚠️ No matching input found for: {question_text}")
                                    continue

                print(f"🔍 Detected input type: {input_type}")

                # **Step 2: Skip Pre-Selected Inputs**
                if input_type in ["text", "textarea"]:
                    existing_value = input_field.get_attribute("value").strip()
                    if existing_value:
                        print(f"⏩ Skipping '{question_text}' (Already filled: {existing_value})")
                        continue

                elif input_type == "dropdown":
                    selected_option = Select(input_field).first_selected_option.text.strip()
                    if selected_option and selected_option.lower() != "select":
                        print(f"⏩ Skipping '{question_text}' (Already selected: {selected_option})")
                        continue

                elif input_type == "radio":
                    if input_field.is_selected():
                        print(f"⏩ Skipping '{question_text}' (Already selected)")
                        continue

                elif input_type == "checkbox":
                    if input_field.is_selected():
                        print(f"⏩ Skipping '{question_text}' (Already checked)")
                        continue

                # **Step 3: Use Predefined Answers Instead of OpenAI**
                if question_text in predefined_answers:
                    ai_answer = predefined_answers[question_text]

                    # Handle dropdown vs. text separately
                    if isinstance(ai_answer, dict):
                        if input_type == "dropdown":
                            ai_answer = ai_answer["dropdown"]
                        elif input_type in ["text", "textarea"]:
                            ai_answer = ai_answer["text"]

                    if ai_answer == "Skip":
                        print(f"⏩ Skipping '{question_text}' (No need to answer)")
                        continue
                else:
                    ai_answer = get_openai_answer(question_text)  # Fallback to AI for unknown questions

                print(f"🤖 Answer: {ai_answer}")

                # **Step 4: Fill in the Answer**
                if input_type in ["text", "textarea"]:
                    input_field.clear()
                    input_field.send_keys(ai_answer)

                elif input_type == "dropdown":
                    select = Select(input_field)
                    best_option = find_best_dropdown_option(select.options, ai_answer)
                    select.select_by_visible_text(best_option)

                elif input_type == "radio":
                    select_best_radio_option(driver, question_label, ai_answer)

                elif input_type == "checkbox":
                    if "yes" in ai_answer.lower():
                        driver.execute_script("arguments[0].click();", input_field)

            except Exception as e:
                print(f"⚠️ Error processing question {index + 1}: {e}")
                continue  # Continue with next question even if one fails

        # **Step 5: Click "Continue"**
        print("🚀 Clicking 'Continue' button...")
        continue_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='continue-button']")
        driver.execute_script("arguments[0].click();", continue_button)

        print("✅ Employer Questions Completed!")
        return True

    except Exception as e:
        print(f"⚠️ Error in Step 2 (Employer Questions): {e}")
        return False



def get_openai_answer(question):
    """
    Uses OpenAI to generate the best answer based on the job question and CV.

    Parameters:
        question (str): The employer's question.
        cv_text (str): The CV content.

    Returns:
        str: AI-generated answer.
    """

    prompt = f"""
    You are a professional job application assistant. 
    Based on the CV below, generate a professional and relevant response to the employer's question.

    Employer Question: "{question}"

    CV Content:
    {CV_TEXT}

    Answer:
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt}]
    )

    return response['choices'][0]['message']['content'].strip()



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




def extract_integer(text):
    """
    Extracts the first integer found in a string.
    If no integer is found, returns '0'.
    """
    match = re.search(r"\b\d+\b", text)
    return match.group(0) if match else "0"