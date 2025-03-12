import requests
import browser_cookie3

# Load saved cookies
cookies = browser_cookie3.chrome(domain_name="seek.com.au")
cookie_dict = {cookie.name: cookie.value for cookie in cookies}

# Create a session and attach cookies
session = requests.Session()
session.cookies.update(cookie_dict)

# Test if login is still valid
profile_url = "https://www.seek.com.au/profile/me"
response = session.get(profile_url)

if "Sign out" in response.text:
    print("✅ You're still logged in!")
else:
    print("⚠️ Session expired. Log in manually & extract cookies again.")