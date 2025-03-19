import re
import os
import json
import openai
import time
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



def apply_step_2_employer_questions(driver):
    questions = extract_questions_and_options(driver)  # Ensure this function provides accurate data
    answers = get_openai_answers(questions)  # Simulated function call

    for item in answers["answers"]:
        question_text = item["question"]
        ai_answer = item["answer"]

        # Find the label element that contains the text
        label = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//label[contains(text(), '{question_text}')]"))
        )

        input_id = label.get_attribute('for')
        print(f"✅ Found label for '{question_text}' with input ID: {input_id}")
        if input_id:
            # Check if the input field is a select or textarea
            input_field = driver.find_element(By.ID, input_id)
            print(f"✅ Found '{input_field}' for '{question_text}'")
            if input_field.tag_name == 'select':
                # Handle select dropdown
                select = Select(input_field)
                # Find and select the option that best matches the AI answer
                for option in select.options:
                    print(f"Checking option: {option.text}")
                    if ai_answer in option.text:
                        select.select_by_visible_text(option.text)
                        break
            elif input_field.tag_name == 'textarea':
                # Handle textarea
                input_field.clear()
                input_field.send_keys(ai_answer)

    # After filling all the fields, click the continue button
    continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
    )
    continue_button.click()

def extract_questions_and_options(driver):
    """
    Extracts employer questions and available input options from the job application form.
    Returns a list of questions with their available answers.
    """
    print("🔍 Extracting employer questions...")

    question_data = []
    question_elements = driver.find_elements(By.CSS_SELECTOR, "label")

    for question_label in question_elements:
        try:
            question_text = question_label.text.strip()
            input_options = []

            # **Find associated dropdown (<select>)**
            try:
                dropdown_container = question_label.find_element(By.XPATH, "ancestor::div/following-sibling::div//select")
                options = dropdown_container.find_elements(By.TAG_NAME, "option")
                input_options = [opt.text.strip() for opt in options if opt.text.strip()]  # Remove empty options

                print(f"✅ Found dropdown for '{question_text}' with options: {input_options}")

            except Exception as e:
                print(f"⚠️ No dropdown found for '{question_text}': {e}")

            # **Find radio button options**
            try:
                radio_buttons = question_label.find_elements(By.XPATH, "ancestor::div/following-sibling::div//input[@type='radio']")
                input_options += [radio.find_element(By.XPATH, "following-sibling::label").text.strip() for radio in radio_buttons]
            except Exception as e:
                print(f"⚠️ No radio buttons found for '{question_text}': {e}")

            # **Find checkbox options**
            try:
                checkboxes = question_label.find_elements(By.XPATH, "ancestor::div/following-sibling::div//input[@type='checkbox']")
                input_options += [checkbox.find_element(By.XPATH, "following-sibling::label").text.strip() for checkbox in checkboxes]
            except Exception as e:
                print(f"⚠️ No checkboxes found for '{question_text}': {e}")

            question_data.append({
                "question": question_text,
                "options": input_options
            })

        except Exception as e:
            print(f"⚠️ Error extracting question: {e}")
            continue

    print(f"🔍 Extracted Questions: {question_data}")
    return question_data

def get_openai_answers(questions):
    """
    Sends employer questions and answer options to OpenAI and returns structured answers.
    """

    predefined_answers = {
        "How many years' experience do you have as a full stack developer?": {"dropdown": "More than 5 years", "text": "13 Years"},
        "How many years' experience do you have as a Ruby on Rails Developer?": {"dropdown": "0-1 years", "text": "1 Year"},
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
        {{"question": "How many years' experience do you have as a full stack developer?", "answer": "13 Years"}},
        {{"question": "What is your expected salary?", "answer": "$100k"}},
        {{"question": "Which of the following programming languages are you experienced in?", "answer": ["Python", "JavaScript", "C++"]}}
      ]
    }}
    """

    response = client.chat.completions.create(
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