import sys
import os
# Set the path to ChromeDriver (Modify as needed)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "/usr/local/bin/chromedriver")