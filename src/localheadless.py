import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import json
import time

if __name__ == "__main__":
    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")    
    options.add_argument("--disable-setuid-sandbox")

    # when running locally, add this this:
    options.add_argument("--proxy-server=socks4://127.0.0.1:1080")

    # macos call without path to chromedriver, then it works
    # linux /usr/bin/chromedriver
    driver = uc.Chrome(headless=False,use_subprocess=True, options=options)
    driver.get("https://iphey.com")
    input()
