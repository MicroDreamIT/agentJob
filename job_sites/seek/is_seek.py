import time
from urllib.parse import urlparse

def is_seek_domain(url):
    parsed_url = urlparse(url)
    return 'seek.com.au' in parsed_url.netloc.lower()

def check_for_redirection(driver, seek_apply_url, timeout=15):
    driver.get(seek_apply_url)

    end_time = time.time() + timeout
    initial_domain = urlparse(seek_apply_url).netloc.lower()

    while time.time() < end_time:
        current_url = driver.current_url
        current_domain = urlparse(current_url).netloc.lower()

        if current_domain != initial_domain:
            print(f"⚠️ Redirected to external URL: {current_url}")
            return False, current_url

        # Short wait before re-checking URL
        time.sleep(0.5)

    # Final check after timeout
    if is_seek_domain(driver.current_url):
        print("✅ Application remains on seek.com.au. Proceeding...")
        return True, driver.current_url
    else:
        print(f"⚠️ Redirected to external URL after timeout: {driver.current_url}")
        return False, driver.current_url
