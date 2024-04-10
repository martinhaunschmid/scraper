from notion import Notion
import logging
from dotenv import load_dotenv
import os
from notifications import Notifications
import json
import pika

class CompaniesWriter:
	def __init__(self):
		logging.info("Setting up")
		load_dotenv()
		self.n = Notifications()
		self.notion = Notion()
		self.setup_queue()

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="companieswriter")  
		
	def update_company(self,data):
		logging.info("Updating company %s" % data["name"])

	def run(self, ch, method, properties,body):
		logging.info("Received Message from Queue")
		data = json.loads(body)
		logging.info("Writing data back to notion for %s" % data['notion_id'])
		self.update_company(data)
		# ch.basic_ack(delivery_tag = method.delivery_tag)

	def loop(self):
		logging.info("Start consuming...")
		self.channel.basic_consume(queue='companieswriter', on_message_callback=self.run, auto_ack=False)
		logging.info("Waiting for messages")
		self.channel.start_consuming()
