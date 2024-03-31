from notifications import Notifications
from notion import Notion
from dotenv import load_dotenv
import pika
import os
import json
import logging
import requests

BASE_URL = "https://api.thecompaniesapi.com/v1/companies/"
HEADERS = {}

class CompaniesAPI:
	def __init__(self):
		load_dotenv()
		self.notion = Notion()
		self.n = Notifications()
		HEADERS['Authorization'] = "Basic " + os.environ.get("COMPANIESAPI_TOKEN")
		self.setup_queue()

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="companiesapi")  

	def load_by_url(self,url):
		logging.info("Loading information for %s" % url)

	def load_by_name(self,name):
		logging.info("Loading information by name: %s" % name)
		logging.warn("Skipping because unreliable")
		return
		# response = requests.get(BASE_URL + "by-name?name="+name, headers=HEADERS)
		# print(response.text)

	def run(self, ch, method, properties,body):
		logging.info("Received Message from Queue")
		data = json.loads(body)
		name = data['name']
		url = data['url']
		if url and url != "":
			result = self.load_by_url(url)
		else:
			result = self.load_by_name(name)
		print(result)
		# ch.basic_ack(delivery_tag = method.delivery_tag)

	def loop(self):
		logging.info("Start consuming...")
		self.channel.basic_consume(queue='companiesapi', on_message_callback=self.run, auto_ack=False)
		logging.info("Waiting for messages")
		self.channel.start_consuming()
