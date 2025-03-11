import requests
import pickle
import os


LOGIN_URL = "https://www.seek.com.au/api/login"
EMAIL = "cristianaanna@gmail.com"
PASSWORD = "gdncqr123$"

COOKIE_FILE = "seek_cookies.pkl"

def login_to_seek_api():
    session = requests.Session()
    login_data = {
        "email": EMAIL,
        "password": PASSWORD,
    }
    response = session.post(LOGIN_URL, data=login_data)
    print('hello',response.status_code)
    if response.status_code == 200 and "dashboard" in response.text:
        print("✅ Login successful! Saving session cookies.")


login_to_seek_api()