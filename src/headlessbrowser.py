import undetected_chromedriver as uc
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
		cookies = json.load(open('cookies.json'))
 
		options = uc.ChromeOptions()
		options.add_argument("--disable-gpu")
		options.add_argument("--no-sandbox")
		options.add_argument("--disable-setuid-sandbox")
		# options.add_argument('--disable-dev-shm-usage')

		self.driver = uc.Chrome(driver_executable_path='/usr/bin/chromedriver',headless=True,use_subprocess=True, options=options)


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
			logging.info("Waiting for redirect...")
			if "authwall" in self.driver.current_url:
				self.n.critical("It seems the Session is invalid")
				exit()
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

	def sleep_seconds(self):
		# first, check if it's feierabend
		now = datetime.now()
		if not(now.weekday() < 5 and 8 <= now.hour < 16):
			# notify first, then return 16h of sleep
			self.n.info("Feierabend, going to sleep...")
			return 60*60*16
		
		if self.counter % 5 == 0:
			sl = 60*10+random.randrange(-180,180)
			logging.info("long sleep: %d" % sl)
			return sl
		
		return random.randrange(5,15)
		

	def run(self, ch, method, properties,body):
		logging.info("Start scraping...")
		self.setup_queue()
		data = json.loads(body)
		notion_id = data["id"]
		linkedin_url = data["url"]
		logging.info("Notion ID: %s" % notion_id)
		logging.info("LinkedIn URL: %s" % linkedin_url)
		try:
			data = self.scrape_profile(notion_id,linkedin_url)
			self.counter += 1
			self.publish(data)
			self.teardown_queue()
			logging.info("Finished, going to sleep before next message")

			time.sleep(self.sleep_seconds())
			ch.basic_ack(delivery_tag = method.delivery_tag)
		except Exception as e:
			self.n.critical("Headlessbrowser crashed, continuing: %s" % e)
			traceback.print_exc()

	def loop(self):
		logging.info("Start consuming...")
		try:
			self.channel.basic_consume(queue='headless', on_message_callback=self.run, auto_ack=False)
			logging.info("Waiting for messages")
			self.channel.start_consuming()
		except Exception as e:
			self.n.critical("Headlessbrowser crashed: %s" % e)
			traceback.print_exc()