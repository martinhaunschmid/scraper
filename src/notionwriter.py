from notion import Notion
import logging
from dotenv import load_dotenv
import os
from notifications import Notifications
import json
import pika
import traceback

class NotionWriter:
	def __init__(self):
		logging.info("Setting up")
		load_dotenv()
		self.n = Notifications()
		self.notion = Notion()
		self.setup_queue()

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="notionwriter")  
	
	def update_companies(self, scraped_data):
		logging.info("Updating or creating companies")
		company_ids = []
		print(scraped_data)
		for i, c in enumerate(scraped_data['experience']):
			if i == 0 or ("job_since_when" in c and c["job_since_when"] != None and "Heute" in c['job_since_when']):
				url = c['url']
				if c['url'] == "":
					url = None
				companydata = {
					'name': c['workplace'],
					'url':url
				}
				companyid = self.notion.write_company_to_database(companydata)
				logging.info("Company ID: %s" % companyid)
				company_ids.append({"id":companyid})

		return company_ids
	
	def update_person(self, data):
		# input: data: all of the data, not only the scraped infos
		logging.info("Updating Person %s" % data['id'])
		self.notion.update_follower(data)

	def run(self, ch, method, properties,body):
		logging.info("Received Message from Queue")
		data = json.loads(body)
		try:
			logging.info("Writing data back to notion for %s" % data['id'])
			scraped_data = data['scraped']
			data['companies'] = self.update_companies(scraped_data)
			self.update_person(data)
			ch.basic_ack(delivery_tag = method.delivery_tag)
		except Exception as e:
			traceback.print_exc()
			print(data)
			self.n.critical("Notionwriter crashed, continuing: %s" % e)

	def loop(self):
		logging.info("Start consuming...")
		self.channel.basic_consume(queue='notionwriter', on_message_callback=self.run, auto_ack=False)
		logging.info("Waiting for messages")
		self.channel.start_consuming()
