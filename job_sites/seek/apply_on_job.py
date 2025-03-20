import re
import os
import json
import time
from difflib import get_close_matches
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from core.config import OPENAI_CLIENT, RESUME_TEXT
from job_sites.for_ai_process.process_cover_letter_openai import process_cover_letter_openai
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

CV_TEXT = os.getenv("CV_TEXT")


def check_for_answer_questions_text(driver):
    # Navigate to the div with data-automation attribute 'job-header'
    job_header = driver.find_element_by_css_selector('div[data-automation="job-header"]')

    # Find all li elements within the job_header context
    list_items = job_header.find_elements_by_css_selector('li')
    print(f'number of header items: {len(list_items)}')

    # Check if there are exactly four li elements
    return len(list_items) == 4


def extract_job_details(driver):
    """Extract job details (Title, Company, Location, Salary, Description) in text format."""
    try:
        job_details_element = driver.find_element(By.CSS_SELECTOR, "div[data-automation='jobDetailsPage']")
        job_text = job_details_element.text.strip()
        return job_text
    except NoSuchElementException:
        print("⚠️ Job details not found.")
        return None


def update_seek_profile(driver):
    continue_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='continue-button']")
    continue_button.click()
    return True


def review_and_submit(driver):
    continue_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='review-submit-application']")
    continue_button.click()
    return True


def apply_on_job(driver, job_id):
    original_window = driver.current_window_handle
    wait = WebDriverWait(driver, 15)
    cover_letter = ''
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

                    if check_for_answer_questions_text(driver):
                        apply_step_2_employer_questions(driver)
                        time.sleep(1)
                    update_seek_profile(driver)
                    time.sleep(1)
                    review_and_submit(driver)

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
        resume_text = RESUME_TEXT
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


def apply_step_2_employer_questions(driver):
    questions = extract_questions_and_options(driver)
    response = get_openai_answers(questions)
    answers = response["answers"]  # This should directly access the list of answer dictionaries

    for question_data in questions:
        question_text = question_data['question']
        input_id = question_data['input_id']

        # Retrieve the answer from OpenAI response matching this question
        answer_info = next((item for item in answers if item['question'] == question_text), None)
        if answer_info:
            answer = answer_info['answer']

            # Process the question based on its type
            input_field = driver.find_element(By.ID, input_id)
            if question_data['input_type'] == 'select':
                select = Select(input_field)
                try:
                    select.select_by_visible_text(answer)
                    print(f"Selected '{answer}' for '{question_text}'")
                except Exception as e:
                    print(f"Failed to select '{answer}' for '{question_text}': {str(e)}")
            elif question_data['input_type'] == 'textarea':
                input_field.clear()
                input_field.send_keys(answer)
                print(f"Filled textarea for '{question_text}' with '{answer}'")
        else:
            print(f"No answer provided for '{question_text}'")

    # Click "Continue"
    time.sleep(2)
    continue_button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='continue-button']")
    continue_button.click()

    print("Employer Questions Completed!")


def extract_questions_and_options(driver):
    questions = []
    labels = driver.find_elements(By.TAG_NAME, 'label')
    for label in labels:
        question_text = label.text.strip()
        input_id = label.get_attribute('for')
        if input_id:
            input_element = driver.find_element(By.ID, input_id)
            input_type = input_element.tag_name
            options = []
            if input_type == 'select':
                select = Select(input_element)
                options = [opt.text for opt in select.options]
            elif input_type == 'input' and input_element.get_attribute('type') == 'radio':
                # Find all radio buttons with the same name attribute
                radios = driver.find_elements(By.NAME, input_element.get_attribute('name'))
                options = [radio.get_attribute('value') for radio in radios]

            question_data = {
                'question': question_text,
                'options': options,
                'input_type': 'select' if input_type == 'select' else input_element.get_attribute('type'),
                'input_id': input_id,
                'name': input_element.get_attribute('name') if input_type == 'input' else None
            }
            questions.append(question_data)
    print(f"🔍 Extracted questions: ", questions)
    return questions


def get_openai_answers(questions):
    predefined_answers = {
        "How many years' experience do you have as a full stack developer?": {"dropdown": "More than 5 years",
                                                                              "text": "13 Years"},
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
        "What city are you based in?": "Perth",
        "Are you an Australian/NZ citizen?": "No",
        "What are your salary expectations?": "$100k",
        "Do you have full working rights in Australia?": "No",
        "Will you require visa sponsorship either now or in the future?": "Yes",
        "How many years' experience do you have using SQL queries?": {"dropdown": "More than 5 years",
                                                                      "text": "13 Years"},
        "Are you willing to work on client site 3 days per week in": "Yes",
        "Are you willing to relocate": "Yes"
    }

    # Format the prompt for OpenAI
    full_prompt = f"""
    Based on my CV:

    {os.getenv("CV_TEXT")}

    And the following employer questions and options:

    {json.dumps(questions, indent=2)}

    Here are my predefined answers:

    {json.dumps(predefined_answers, indent=2)}

    Please return the best-matching answers in structured JSON format. If the predefined answer is slightly different from the dropdown/checkbox options, select the closest match.

    Example output:
    {{
      "answers": [
        {{"question": "How many years' experience do you have as a full stack developer?", 
        "answer": "13 Years"}},
        {{"question": "What is your expected salary?", "answer": "$100k"}},
        {{"question": "Which of the following programming languages are you experienced in?", "answer": ["Python", "JavaScript", "C++"]}}
      ]
    }}
    
    Are you willing to work or relocate in any city and country for the job? is always Yes. 
    """

    response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are an AI assistant helping with job applications."},
                  {"role": "user", "content": full_prompt}],
        temperature=0.5,
        max_tokens=1000
    )

    # ✅ Extract raw response content
    ai_response = response.choices[0].message.content.strip()

    # 🔍 Debug: Print raw response
    print(f"🔍 OpenAI Raw Response: {ai_response}")

    # ✅ Extract JSON using regex
    match = re.search(r"\{.*\}", ai_response, re.DOTALL)

    if match:
        json_text = match.group(0)  # Extract JSON portion
        try:
            return json.loads(json_text)  # ✅ Parse extracted JSON
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON Decode Error: {e}")
            print(f"🔍 Extracted JSON: {json_text}")
            return {"answers": []}  # Return empty structure instead of crashing
    else:
        print("⚠️ No valid JSON found in OpenAI response!")
        return {"answers": []}  # Return default empty response


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
