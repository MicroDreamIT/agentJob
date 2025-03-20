import openai
import os
from core.config import OPENAI_CLIENT


def process_cover_letter_openai(job_details):
    """
    Generate a cover letter using OpenAI API based on job details.

    Parameters:
        job_details (str): The extracted job description and details.

    Returns:
        str: The generated cover letter.
    """
    full_prompt = f"""
    Based on the following job description:

    {job_details}

    And my CV:

    {os.getenv("CV_TEXT")}

    Write a personalized, concise, and professional cover letter that highlights my skills and experience for this role.
    Use a simple, humble, unique and growth mindset approach of Dr Carol. Reflect eager to learn, contribute, share and grow.
    
    
    Please dont write subject.
    try to start with the name, or the company name, Dear ....
    """

    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional HR assistant helping to craft cover letters."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,  # Adjust creativity level
            max_tokens=300
        )

        cover_letter = response.choices[0].message.content.strip()
        # print(cover_letter)
        return cover_letter

    except openai.OpenAIError as e:
        print(f"⚠️ OpenAI API Error: {e}")
        return "Error generating cover letter."
