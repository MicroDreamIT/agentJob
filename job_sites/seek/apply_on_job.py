import re
import os
import json
import time
from difflib import get_close_matches

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from core.config import OPENAI_CLIENT, RESUME_TEXT
from core.database import FailedJob, open_session
from job_sites.for_ai_process.process_cover_letter_openai import process_cover_letter_openai
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

CV_TEXT = os.getenv("CV_TEXT")


def check_for_answer_questions_text(driver):
    # Navigate to the div with data-automation attribute 'job-header'
    job_header = driver.find_element(By.CSS_SELECTOR, 'div[data-automation="job-header"]')

    # Find all li elements within the job_header context
    list_items = job_header.find_elements(By.CSS_SELECTOR, 'li')

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
    try:
        # Locate the button
        button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='continue-button']"))
        )

        # Use ActionChains to scroll to the button and focus on it
        ActionChains(driver).move_to_element(button).perform()

        # Wait until the element is definitely clickable after moving to it
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='continue-button']"))
        )

        # Click the button
        button.click()
        print("✅ Update Seek Profile Completed!")
    except Exception as e:
        print(f"Failed to update Seek profile: {str(e)}")
        return False

    return True


def review_and_submit(driver):
    try:
        # Locate the submit button using its CSS selector and test ID
        button = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='review-submit-application']"))
        )

        # Use ActionChains to scroll to the button and focus on it
        ActionChains(driver).move_to_element(button).perform()

        # Ensure the button is clickable before proceeding
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='review-submit-application']"))
        )

        # Click the submit button
        button.click()
        print("✅ Review and Submit Completed!")
    except Exception as e:
        print(f"Failed to complete review and submit: {str(e)}")
        return False

    return True


def apply_on_job(driver, job_id, job_link):
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
                        print("✅ Step 2 in progress...")
                        apply_step_2_employer_questions(driver)

                    time.sleep(3)
                    print("➡️ update_seek_profile in progress...")
                    update_seek_profile(driver)
                    time.sleep(3)
                    print("➡️ review_and_submit in progress...")
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
        session = open_session()
        failed_job = FailedJob(
            provider='SEEK',
            provider_id=job_id,
            link=job_link,  # Ensure you retrieve and store the job link
            error_message=str(e)
        )
        session.add(failed_job)
        session.commit()
        session.close()
        return [False, str(e)]

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
        time.sleep(5)
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
    print("✅ Step 2 in inside...")
    questions = extract_questions_and_options(driver)
    print(f"🔍 Extracted questions: ", questions)
    response = get_openai_answers(questions)
    print(f"🔍 OpenAI Raw Response: {response}")

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
                if select.first_selected_option.text.strip():
                    print(f"Skipping '{question_text}' as it is already selected.")
                else:
                    select.select_by_visible_text(answer)
                    print(f"Selected '{answer}' for '{question_text}'")
            elif question_data['input_type'] == 'radio':
                select_radio_option(driver, question_data, answer)

            elif question_data['input_type'] == 'textarea':
                input_field.clear()
                input_field.send_keys(answer)
                print(f"Filled textarea for '{question_text}' with '{answer}'")
            elif question_data['input_type'] == 'text':
                input_field.clear()
                input_field.send_keys(answer)
                print(f"Filled textarea for '{question_text}' with '{answer}'")
        else:
            print(f"No answer provided for '{question_text}'")

    time.sleep(2)
    button = driver.find_element(By.CSS_SELECTOR, "button[data-testid='continue-button']")
    ActionChains(driver).move_to_element(button).perform()

    # Wait until the element is definitely clickable
    WebDriverWait(driver, 2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='continue-button']"))
    )
    button.click()

    print("✅ Employer Questions Completed!")


def select_radio_option(driver, question_data, answer):
    base_input_id = question_data['input_id']
    question_text = question_data['question']

    try:
        # Construct the XPath to locate the correct radio button by text label associated with it
        xpath_expression = f"//input[starts-with(@id, '{base_input_id}_') and @type='radio']"
        radio_buttons = driver.find_elements(By.XPATH, xpath_expression)

        # Find the correct radio button based on the label text
        for radio in radio_buttons:
            # Locate the label corresponding to the radio button to check its text
            label = driver.find_element(By.XPATH, f"//label[@for='{radio.get_attribute('id')}']")
            if label.text.strip().lower() == answer.lower():
                # Click the radio button if it is not already selected
                if not radio.is_selected():
                    ActionChains(driver).move_to_element(radio).click().perform()
                    print(f"Selected radio button '{answer}' for '{question_text}'")
                    break
        else:
            print(f"No radio button found matching answer '{answer}' for '{question_text}'")

    except NoSuchElementException:
        print(f"Radio button with base ID '{base_input_id}' and answer '{answer}' not found for '{question_text}'")
    except Exception as e:
        print(f"An error occurred while trying to select the radio button for '{question_text}': {e}")


def extract_questions_and_options(driver):
    print("✅ Step 2 extracting questions...")
    questions = []
    wait = WebDriverWait(driver, 10)

    # Handle fieldsets for radio or checkbox groups (optional existence)
    fieldsets = driver.find_elements(By.CSS_SELECTOR, 'fieldset[role="radiogroup"]')
    if fieldsets:
        for fieldset in fieldsets:
            try:
                legend = fieldset.find_element(By.TAG_NAME, 'legend')
                question_text = legend.text.strip() if legend else "No question text found"

                inputs = fieldset.find_elements(By.CSS_SELECTOR, 'input[type="radio"], input[type="checkbox"]')
                options = []
                for input_elem in inputs:
                    try:
                        label = driver.find_element(By.CSS_SELECTOR, f'label[for="{input_elem.get_attribute("id")}"]')
                        option_text = label.text.strip()
                    except NoSuchElementException:
                        option_text = "Label not found"

                    options.append({
                        'value': input_elem.get_attribute('value'),
                        'label': option_text,
                        'id': input_elem.get_attribute('id'),
                        'type': input_elem.get_attribute('type')
                    })

                questions.append({
                    'question': question_text,
                    'options': options,
                    'input_type': inputs[0].get_attribute('type') if inputs else 'unknown',
                    'fieldset_id': fieldset.get_attribute('id'),
                    'input_id': fieldset.get_attribute('id'),
                })
            except NoSuchElementException as e:
                print(f"⚠️ Error processing fieldset: {e}")
    else:
        print("ℹ️ No radio groups found, skipping radio group questions.")

    # Handle selects, text inputs, and textareas
    inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea, select')
    for input_elem in inputs:
        try:
            label = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{input_elem.get_attribute("id")}"]')))
            question_text = label.text.strip() if label else "No label found"

            if input_elem.tag_name == 'select':
                select_obj = Select(input_elem)
                options = [{'value': opt.get_attribute('value'), 'label': opt.text} for opt in select_obj.options]
                input_type = 'select'
            elif input_elem.tag_name == 'textarea':
                options = []
                input_type = 'textarea'
            else:  # input type="text"
                options = []
                input_type = 'text'

            questions.append({
                'question': question_text,
                'options': options,
                'input_type': input_type,
                'input_id': input_elem.get_attribute('id'),
                'name': input_elem.get_attribute('name')
            })
        except NoSuchElementException as e:
            print(f"Error processing input: {e}")
    return questions


def preset_test_data():
    return {
        "answers": [
            {
                "question": "Are you open to working in a Sydney based office 2-3 times per week?",
                "answer": "Yes"
            },
            {
                "question": "Which of the following statements best describes your right to work in Australia?",
                "answer": "I require sponsorship to work for a new employer (e.g. 482, 457)"
            }
        ]
    }


def get_openai_answers(questions):
    predefined_answers = {
        "Experience in full stack developer?": {"dropdown": "More than 5 years",
                                                                              "text": "13 Years"},
        "Experience in front end software developer?": {"dropdown": "More than 5 years",
                                                                              "text": "13 Years"},
        "Experience in back end software developer?": {"dropdown": "More than 5 years",
                                                                              "text": "13 Years"},
        "Experience in Ruby in Rails Developer?": {"dropdown": "Less than 1 year",
                                                                                 "text": "1 Year"},
        "Experience in data scientist or data analyst or data science or data engineering?": {"dropdown": "3 year",
                                                                                 "text": "3 Year"},
        "Which of the following statements best describes your right to work in Australia?": {
            "dropdown": "I require sponsorship to work for a new employer (e.g. 482, 457)",
            "text": "I require sponsorship to work for a new employer (e.g. 482, 186)"},
        "Do you have a current Australian driver's licence?": "No",
        "Do you own or have regular access to a car?": "Yes",
        "Experience in ServiceNow Developer?": "No experience",
        "Do you hold Australian Security Clearance?": "No",
        "How much notice are you required to give your current employer?": "1 week",
        "Experience in C++ Developer?": "2",
        "Experience in Java Software Engineer?": "1",
        "Have you worked in a role which requires CSS development experience?": "Yes",
        "Experience in software engineer?": "5",
        "Experience do you have in a DevOps role?": "1",
        "What city are you based in?": "Perth",
        "Are you an Australian/NZ citizen?": "No",
        "What are your salary expectations?": "$100k",
        "Do you have full working rights in Australia?": "No",
        "Will you require visa sponsorship either now or in the future?": "Yes",
        "Experience do you have using SQL queries?": {"dropdown": "More than 5 years",
                                                                      "text": "13 Years"},
        "Are you willing to work on client site 3 days per week in": "Yes",
        "Are you willing to relocate": "Yes",
        "Experience in applications developer?": {"dropdown": "More than 5 years",
                                                                                 "text": "13 Years"},
        "Experience in .NET developer?": {"dropdown": "Less than 1 year",
                                                                        "text": "1 Year"},
        "Experience in NodeJs developer?": {"dropdown": "Less than 1 year",
                                                                          "text": "1 Year"},
        "Experience do you have working in an agile environment?": {"dropdown": "More than 5 years",
                                                                                    "text": "13 Years"},
        "Have you completed a qualification in engineering?": {"dropdown": "Bachelor's degree",
                                                               "text": "Bachelor's degree"},
        "Experience in eCommerce Specialist?": {"dropdown": "More than 5 years",
                                                                                 "text": "13 Years"},
        "Experience in Implementation Specialist?": {"dropdown": "More than 5 years", "text": "13 Years"},
        "Experience in Engineering Lead?":{"dropdown": "More than 5 years", "text": "13 Years"},
        "Artificial Intelligence experience": {"dropdown": "More than 2 years", "text": "3 Years"},

    }
    print("✅ Step 2 in sending response to openai...")
    # if app_env == 'test': return preset_test_data()

    # Format the prompt for OpenAI
    full_prompt = f"""
    Based on my CV:

    {os.getenv("CV_TEXT")}

    And the following employer questions and options:

    {json.dumps(questions, indent=2)}

    Here are my predefined answers:

    {json.dumps(predefined_answers, indent=2)}

    Please return the best-matching answers of only employer questions in structured JSON format. If the predefined answer is slightly different from the dropdown/checkbox options, select the closest match from the CV.
    with input id or id for the input field as well.
    If the question is not found in the predefined answers or CV, then select at least 1 year value from the dropdown, or write n/a or 1.
    As you find in my CV I have 13 years of experience in project management, software development, and team leadership.
    Anything about Security Clearance, select No. or write no
    Example output:
    {{
      "answers": [
        {{"question": "Experience in full stack developer?", 
        "answer": "13 Years"}},
        {{"question": "What is your expected salary?", "answer": "$100k"}},
        {{"question": "Which of the following programming languages are you experienced in?", "answer": ["Python", "JavaScript", "C++"]}}
      ]
    }}
    
    Are you willing to work or relocate in any city and country for the job? is always Yes. 
    """

    response = OPENAI_CLIENT.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[{"role": "system", "content": "You are an AI assistant helping with job applications."},
                  {"role": "user", "content": full_prompt}],
        temperature=0.5,
        max_tokens=1024
    )

    # ✅ Extract raw response content
    ai_response = response.choices[0].message.content.strip()

    # 🔍 Debug: Print raw response


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
