from selenium import webdriver
from selenium.webdriver.chrome.service import Service
# Path to your ChromeDriver
chrome_driver_path = "/usr/local/bin/chromedriver"

def login_to_seek():
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.seek.com.au/login")
    input("🔑 Log in manually, then press Enter...")

if __name__ == "__main__":
    login_to_seek()