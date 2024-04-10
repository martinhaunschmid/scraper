from notion import Notion
import logging
from dotenv import load_dotenv
from notifications import Notifications
import pika
import traceback
import os
import json


class CompaniesLoader:
	def __init__(self):
		logging.info("Setting up")
		load_dotenv()
		self.n = Notifications()
		self.setup_queue()

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="enrichcompanies")

	def teardown_queue(self):
		self.queue.close()

	def load_from_notion(self):
		logging.info("Start loading from notion")
		n = Notion()
		companies = n.load_companies_to_enrich()

		# build objects for message queue
		for c in companies:
			msg = {
				"name": c["properties"]["Name"]["title"][0]["text"]["content"],
				"url": c["properties"]["URL"]["url"],
				"notion_id": c["id"]
			}
			logging.info("Adding %s to queue" % msg["name"])
			self.channel.basic_publish(exchange='', routing_key='enrichcompanies', body=json.dumps(msg))
	
	def run(self):
		self.load_from_notion()
		
	def loop(self):
		try:
			self.run()
			logging.info("Going to sleep...")
		except Exception as e:
			self.n.critical("NotionLoader crashed: %s" % e)
