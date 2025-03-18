import openai
import os

# Load OpenAI API Key from environment variables (Recommended)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def process_cover_letter_openai(job_details):
    """
    Generate a cover letter using OpenAI API based on job details.

    Parameters:
        job_details (str): The extracted job description and details.

    Returns:
        str: The generated cover letter.
    """
    if not OPENAI_API_KEY:
        raise ValueError("⚠️ OpenAI API key not found! Please set OPENAI_API_KEY environment variable.")

    prompt = f"""
    I am applying for the following job:

    {job_details}

    Write a professional and personalized cover letter highlighting my relevant skills and experience.
    Keep it concise and engaging.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional HR assistant helping to craft cover letters."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Adjust creativity level
            max_tokens=500
        )

        cover_letter = response['choices'][0]['message']['content']
        return cover_letter.strip()

    except openai.error.OpenAIError as e:
        print(f"⚠️ OpenAI API Error: {e}")
        return "Error generating cover letter."

