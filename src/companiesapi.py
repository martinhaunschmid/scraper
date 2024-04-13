from notifications import Notifications
from notion import Notion
from dotenv import load_dotenv
import pika
import os
import json
import logging
import requests
import time

GET_DOMAIN_URL = "company.clearbit.com/v1/domains/find?name="
ENRICH_URL = "company.clearbit.com/v2/companies/find?domain="
HEADERS = {}

# Clearbit
# curl 'https://company.clearbit.com/v1/domains/find?name=Ripka+-+Security+Consulting' -u SK

class CompaniesAPI:
	def __init__(self):
		load_dotenv()
		self.notion = Notion()
		self.n = Notifications()
		# HEADERS['Authorization'] = "Basic " + os.environ.get("COMPANIESAPI_TOKEN")
		self.setup_queue()

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="enrichcompanies")
	
	def publish(self,data):
		logging.info("Publishing data to write back to notion for %s" % data['name'])
		# Writes to queue
		self.channel.queue_declare(queue='companieswriter')
		self.channel.basic_publish(exchange='', routing_key='companieswriter', body=json.dumps(data))

	def get_url(self,name):
		logging.info("Getting URL of company")
		response = requests.get("https://%s@%s" % (os.environ.get("CLEARBIT_KEY"), GET_DOMAIN_URL) + name)
		if not "error" in response.text:
			return json.loads(response.text)["domain"]
		else:
			print(response.text)
			return ""

	def load_by_url(self,domain, data):
		logging.info("Loading information for %s" % domain)
		response = requests.get("https://%s@%s%s"  % (os.environ.get("CLEARBIT_KEY"), ENRICH_URL, domain))
		data["content"] = response.text
		data["url"] = domain
		company = json.loads(response.text)

		if "description" in company:
			data["description"] = company["description"]

		if "metrics" in company:
			for f in ["estimatedAnnualRevenue","employees"]:
				data[f] = company["metrics"][f]

		if "category" in company:
			for f in ["sector","industryGroup","industry","subIndustry"]:
				data[f] = company["category"][f]

		if "logo" in company:
			data["logo"] = company["logo"]
		
		if "geo" in company:
			data["country"] = company["geo"]["country"]

		if "tags" in company:
			tags = []
			for t in company["tags"]:
				tags.append({"name":t, "color":"gray"})
			data["tags"] = tags

		return data


	def run(self, ch, method, properties,body):
		data = json.loads(body)
		name = data["name"]
		url = data["url"]
		logging.info("Received Message from Queue: %s" % name)
		if not url or url == "Null":
			logging.debug("Getting URL first")
			url = self.get_url(name)
			logging.info("Found URL: %s" % url)

			if not url:
				# didn't find url, set company to problematic
				self.notion.set_company_to_problem(data['notion_id'])
				logging.error("Did not find domain for company %s, set it to problematic" % name)
				ch.basic_ack(delivery_tag = method.delivery_tag)
				return

		result = self.load_by_url(url, data)
		self.publish(result)
		time.sleep(30)
		ch.basic_ack(delivery_tag = method.delivery_tag)

	def loop(self):
		logging.info("Start consuming...")
		self.channel.basic_consume(queue='enrichcompanies', on_message_callback=self.run, auto_ack=False)
		logging.info("Waiting for messages")
		self.channel.start_consuming()
