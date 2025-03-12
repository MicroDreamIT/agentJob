import browser_cookie3

# Extract Seek session cookies from Chrome (or change to Firefox, Edge)
cookies = browser_cookie3.chrome(domain_name="seek.com.au")

# Convert cookies to dictionary format
cookie_dict = {cookie.name: cookie.value for cookie in cookies}

# Print extracted cookies
print("Your Seek Session Cookies:", cookie_dict)