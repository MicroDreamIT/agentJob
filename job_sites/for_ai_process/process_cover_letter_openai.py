import openai
import os

from core.config import OPENAI_API_KEY, CV_TEXT


# ✅ Create OpenAI client instance
client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))

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
    Use a unique and growth mindset approach.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional HR assistant helping to craft cover letters."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7,  # Adjust creativity level
            max_tokens=500
        )

        cover_letter = response.choices[0].message.content.strip()
        print(cover_letter)
        return cover_letter

    except openai.OpenAIError as e:
        print(f"⚠️ OpenAI API Error: {e}")
        return "Error generating cover letter."

if __name__ == '__main__':
    job_details = """Full Stack Developer x 2

Redcat Pty Ltd 
View all jobs
Cremorne, Melbourne VIC
Developers/Programmers (Information & Communication Technology)
Full time
Posted 2m ago
How you match
1 skill or credential matches your profile
 MySQL
Show all⁠
About the Company

The Redcat Hospitality IT Platform offers business-management software and hardware solutions that cover web and mobile applications including online ordering and loyalty systems, tightly integrated with the point of sale (POS) and back of house applications. Redcat also supports multiple integrations to enhance the offerings suite for our clients.

We work with amazing hospitality brands like Boost Juice, Nando's, Chatime, Grill'd, Schnitz just to name a few, to provide them with a hospitality IT platform that provides a seamless customer experience.

We're a company that puts culture first and are looking for people to help us continue our growth!

Due to continued growth and expansion, we are excited to hire a Business Analyst / Product Owner to complement our existing team.  

The Role
We are looking for 2 Full Stack Developers to join our expanding team. 
A key focus will be to create high-quality, scalable, and reliable server-side solutions and web applications that align with the business objectives and goal

Working with your team, you will cooperatively solve issues and maintain a positive and cohesive working environment. 

You will also mentor and provide guidance to other web developers in the team

Responsibilities 

Software Development:
Design, develop, test, and deploy high-quality software solutions.
Write clean, maintainable, and efficient code following best practices.
Be responsible for maintaining, expanding, and scaling our product
Participate in code reviews to ensure code quality and share knowledge with team members.
Create and maintain software documentation
Implementing security measures to protect data and applications from vulnerabilities and attacks.
Integrating third-party services and APIs.
Creating and maintaining APIs (Application Programming Interfaces) for front-end and other systems to interact with.
Problem-Solving and Innovation:

Display problem-solving skills, cultivate positive relationships, and have clear communication and coordination when completing tasks 
Articulate and present with high ability, complex concepts clearly and concisely 
Gather and refine specifications and requirements based on technical needs
Leadership and Teamwork

Cooperate with other developers to create a cohesive team and product 
Mentoring junior and mid-level developers, providing guidance and support to help them grow.
About You

Ideally you will have at least 5 years’ experience in the industry in a leadership or senior role
A tertiary level degree in computer science or equivalen
Understanding of one or more of the following languages Python, JavaScript / Typescript , React, React native
Understanding of SQL (MySQL or Mariadb an advantage)
 
Our Values

Integrity - We stand for integrity

Teamwork - Together we shine

Customer Centric - We have the customer at the Heart

Innovation - Be the agent of change

Accountability - We deliver what we promise

Why Join Us?

To attract the best people, we understand that it takes more than just a generous salary. To keep an engaged and motivated team, we also provide career growth opportunities, work flexibility, autonomy, and a high-performance culture – all to ensure that you can achieve your best – both inside and away from work.

Benefits Include

A day off for your birthday 🎁
Regular social events 🎉
Access to twice per week dedicated bootcamp training 💪🏼
Sponsored professional development 👩🏻‍💻
A relaxed and friendly team culture 🤗

Employer questions
Your application will include the following questions:
How many years' experience do you have as a full stack developer?
Which of the following programming languages are you experienced in?
Have you worked in a role which requires a sound understanding of the software development lifecycle?
How many years' experience do you have using SQL queries?
What's your expected annual base salary?
Which of the following statements best describes your right to work in Australia?
How many years' experience do you have in a software development role?
How would you rate your English language skills?"""
    process_cover_letter_openai(job_details)