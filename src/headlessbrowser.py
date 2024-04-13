import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import json
import pika
import traceback
import random
from datetime import datetime
from notifications import Notifications

class HeadlessBrowser:

	def __init__(self):
		logging.info("Setting up...")

		# os.environ
		load_dotenv()

		# queue
		self.setup_queue()
		
		# Headless Driver
		cookies = [{'domain': '.linkedin.com', 'httpOnly': True, 'name': 'fptctx2', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'taBcrIH61PuCVH7eNCyH0MJojnuUODHcZ6x9WoxhgClCw99e%252fZaCGnYrmIQlIx12sFMKl4MqWvcbhvuu1NOZRX6RUjDsygU2MDvSn8eLWm7%252ffSkH%252fw1zffTvlwcpCVjX3630OlcaMZVGz8eUSo%252bjc4jphnhzYcEq0jDR2iqoN45jvLf6g2NJrASsxWLTE23yZHME0UJ1r07VAsfPGeAuKa534t1IYMVCS0CItMz0XNqq7pfpVu9hhQHT0D%252bUGSd7DZLQ3BTqoA9ktxiqJ5Gd%252b%252fkAQ2za0q4A1qCB59kwHecxRbU7QtSY%252bJbJEOCDRJxtj27onqybxnwcFkf8M%252bOY9R5WfDgLFUebs%252b66VCqLe4s%253d'}, {'domain': '.linkedin.com', 'expiry': 1740947422, 'httpOnly': True, 'name': 'dfpfpt', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '5282537129464e009cac7ebc83ddd55b'}, {'domain': '.www.linkedin.com', 'expiry': 1724959819, 'httpOnly': False, 'name': 'li_theme_set', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'app'}, {'domain': '.www.linkedin.com', 'expiry': 1724959819, 'httpOnly': False, 'name': 'li_theme', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'light'}, {'domain': '.www.linkedin.com', 'expiry': 1710621019, 'httpOnly': False, 'name': 'timezone', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'Europe/Vienna'}, {'domain': '.www.linkedin.com', 'expiry': 1717187414, 'httpOnly': False, 'name': 'JSESSIONID', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '"ajax:2205511660193169357"'}, {'domain': '.linkedin.com', 'expiry': 1709495548, 'httpOnly': False, 'name': 'lidc', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '"b=VB42:s=V:r=V:a=V:p=V:g=5129:u=4:x=1:i=1709411415:t=1709495547:v=2:sig=AQE7asQJqhtcVWDGok1qbqOnwCKrpw7C"'}, {'domain': '.linkedin.com', 'expiry': 1724963416, 'httpOnly': False, 'name': 'li_mc', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'MTs0MjsxNzA5NDExNDE1OzI7MDIxwTd8lU4CYg21YQesuvDao4M3uq9GmSeD2MTohNvYw3c='}, {'domain': '.linkedin.com', 'httpOnly': False, 'name': 'lang', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'v=2&lang=de-de'}, {'domain': '.linkedin.com', 'expiry': 1717187414, 'httpOnly': False, 'name': 'liap', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'true'}, {'domain': '.www.linkedin.com', 'expiry': 1740947414, 'httpOnly': True, 'name': 'li_at', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'AQEDAUENqOIERrJ6AAABjgDcMbkAAAGOJOi1uU4AGuEF5VqNWdgoyDq07Q56w5EsaZ40s7YEt6mILdxpQNFC8qUXSKt1LOyoLxqUbkCKRpSambmqkjUhnX9nQM9ND3SquXnxDPBzOhvioPjBf59ZNmpL'}, {'domain': '.linkedin.com', 'expiry': 1740947416, 'httpOnly': False, 'name': 'bcookie', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '"v=2&206544ea-a0d9-4a74-88fe-621dbe9a603b"'}, {'domain': 'www.linkedin.com', 'expiry': 1740947404, 'httpOnly': False, 'name': 'li_alerts', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'e30='}, {'domain': '.linkedin.com', 'expiry': 1724963404, 'httpOnly': False, 'name': 'li_gc', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'MTswOzE3MDk0MTE0MDM7MjswMjEpj3JdCxk6UKLpnCKYoRqSlRpSYhfEViSOI88oKXy0hA=='}, {'domain': '.www.linkedin.com', 'expiry': 1740947416, 'httpOnly': True, 'name': 'bscookie', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '"v=1&20240302203003c1b3968d-ee07-4f6a-815f-a0adc336cd70AQFq7Vrtmij9oZHy-knEPI4HI3nWrQPl"'}]
		self.driver = uc.Chrome(headless=False,use_subprocess=True)
		self.driver.get("https://linkedin.com")
		logging.info("Adding Cookies")
		for cookie in cookies:
			self.driver.add_cookie(cookie)

		# Notifications
		self.n = Notifications()

		self.counter = 0

		logging.info("Done")

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="gpt")
		self.channel.queue_declare(queue="headless")

	def teardown_queue(self):
		self.queue.close()

	def data_from_html(self,html):
		soup = BeautifulSoup(html, "html.parser")
		profile_text = ""
		for l in soup.find(class_="body").get_text().split("\n"):
			if l.strip() != "":
				profile_text = profile_text + "%s" % l
		return profile_text
	
	def scrape_profile(self,notion_id,linkedin_url):
		self.driver.get(linkedin_url)
		while "miniProfileUrn" in self.driver.current_url:
			logging.debug("Waiting for redirect...")
			time.sleep(1)
		# Sleep for good measure
		time.sleep(10)

		data = {
			'profile_url': self.driver.current_url,
			'slug': self.driver.current_url.split("/")[4],
			'notion_id': notion_id,
			'profile_text': self.data_from_html(self.driver.page_source)
		}

		with open("%s/%s.txt" % (os.environ.get("WORKSPACE"), data['slug']), 'w') as f:
			f.write(data['profile_text'])

		logging.info("Profile URL: %s" % self.driver.current_url)
		return data
		
	def publish(self, data):
		logging.info("Publishing scraped data to Queue for User %s" % data['slug'])
		# Writes to queue
		self.channel.basic_publish(exchange='', routing_key='gpt', body=json.dumps(data))
		

	def run(self, ch, method, properties,body):
		while int(datetime.now().strftime("%H")) > 18:
			logging.info("It's after 18h, sleeping an hour")
			time.sleep(3600)


		logging.info("Start scraping...")
		self.setup_queue()
		data = json.loads(body)
		notion_id = data["id"]
		linkedin_url = data["url"]
		logging.info("Notion ID: %s" % notion_id)
		logging.info("LinkedIn URL: %s" % linkedin_url)
		
		data = self.scrape_profile(notion_id,linkedin_url)
		self.counter += 1
		self.publish(data)
		self.teardown_queue()
		logging.info("Finished, going to sleep before next message")

		
		if self.counter % 5 == 0:
			sl = 60*10+random.randrange(-180,180)
			logging.info("long sleep: %d" % sl)
			time.sleep(sl)
		time.sleep(random.randrange(5,15))
		ch.basic_ack(delivery_tag = method.delivery_tag)

	def loop(self):
		logging.info("Start consuming...")
		try:
			self.channel.basic_consume(queue='headless', on_message_callback=self.run, auto_ack=False)
			logging.info("Waiting for messages")
			self.channel.start_consuming()
		except Exception as e:
			# self.n.critical("Headlessbrowser crashed: %s" % e)
			traceback.print_exc()
			pass