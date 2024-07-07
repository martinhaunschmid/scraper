import undetected_chromedriver as uc
import time
import json

cookies = json.load(open('cookies.json'))

options = uc.ChromeOptions()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox")
driver = uc.Chrome(driver_executable_path='/usr/bin/chromedriver',headless=True,use_subprocess=True, options=options)

driver.get("https://www.linkedin.com")
time.sleep(5)

for cookie in cookies:
    driver.add_cookie(cookie)
time.sleep(5)
driver.get("https://www.linkedin.com/in/ACoAACaCLKwBrC1_k2NW0bFLv0HKkujqq1UztDM?miniProfileUrn=urn%3Ali%3Afs_miniProfile%3AACoAACaCLKwBrC1_k2NW0bFLv0HKkujqq1UztDM")

while True:
    print(driver.get_cookies())
    print("\n\n\n")
    time.sleep(30)