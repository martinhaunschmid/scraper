import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

if __name__ == "__main__":
    print("Trying to log in as %s..." % os.environ.get("LI_USER"))
    print("Make sure proxy to `automation` is running")

    options = uc.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")    
    options.add_argument("--disable-setuid-sandbox")

    # when running locally, add this this:
    # options.add_argument("--proxy-server=socks4://127.0.0.1:1080")

    # macos call without path to chromedriver, then it works
    # linux /usr/bin/chromedriver
    driver = uc.Chrome(headless=False,use_subprocess=True, options=options)

    driver.get("https://linkedin.com")
    time.sleep(3)
    driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")
    time.sleep(5)
    # #username #password
    user = driver.find_element(By.ID, "username")
    user.send_keys(os.environ.get("LI_USER"))
    time.sleep(3)
    passwd = driver.find_element(By.ID, "password")
    passwd.send_keys(os.environ.get("LI_PASS"))
    passwd.send_keys(Keys.RETURN)
    if "challenge" in driver.current_url:
        print("Challenged!")
        code = input("Input the code sent to the email address!")
        print("TODO: NOT IMPLEMENTED")

    print("Done.")
    print(driver.get_cookies())
    with open('cookies.json', 'w') as f:
        f.write(json.dumps(driver.get_cookies()))