from notion import Notion
import logging
from dotenv import load_dotenv
import os
from notifications import Notifications
import pika
import json


class NotionLoader:
	def __init__(self):
		logging.info("Setting up")
		load_dotenv()
		self.n = Notifications()
		self.setup_queue()

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="headless")

	def teardown_queue(self):
		self.queue.close()		

	def publish(self,data):
		logging.info("Publishing profile to scrape")
		# Writes to queue
		self.channel.basic_publish(exchange='', routing_key='headless', body=json.dumps(data))

	def load_from_notion(self):
		logging.info("Start loading from notion")
		n = Notion()
		followers = n.load_users_to_scrape()

		for f in followers:
			data = {
				"id":f["id"],
				"url":f["properties"]["URL"]["url"],
			}
			self.publish(data)
			n.set_follower_to_scraping(f["id"])
			logging.info("sent %s to queue" % data["id"])
	
	def run(self):
		self.load_from_notion()
		
	def loop(self):
		try:
			self.run()
			logging.info("Going to sleep...")
		except Exception as e:
			self.n.critical("NotionLoader crashed: %s" % e)
