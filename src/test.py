from notion import Notion
import logging
import argparse
from dotenv import load_dotenv
import pika
import os
import json

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["gpt","headlessbrowser","notionwriter", "companiesapi"])
args = parser.parse_args()

data = {
	'profile_url': "https://www.linkedin.com/in/otrip/",
	'slug': 'otrip',
	'notion_id': "4d115f82-e64a-4926-b762-30fd3b13bbf5"
}

companydata = {
	'name': 'SecuBridge Consulting GmbH',
	'url': None
}

def add_profile_text(data):
	with open("../workspace/otrip.txt", 'r') as f:
		data['profile_text'] = f.read()

def add_profile_json(data):
	with open("../workspace/otrip.json", 'r') as f:
		data['scraped'] = json.loads(f.read())

if __name__ == "__main__":
	logging.info("Running some tests")
	n = Notion()
	load_dotenv()

	queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
	channel = queue.channel()

	match args.mode:
		case 'headlessbrowser':
			logging.info("NOT IMPLEMENTED YET")
		case 'gpt':
			logging.info("Sending queue message to gpt component")
			channel.queue_declare(queue="gpt")
			# add test data for this stage
			add_profile_text(data)
			# send 
			channel.basic_publish(exchange='', routing_key='gpt', body=json.dumps(data))
		case 'notionwriter':
			logging.info("Sending queue message to notionwriter")
			# updating data
			add_profile_text(data)
			add_profile_json(data)
			channel.queue_declare(queue='notionwriter')
			channel.basic_publish(exchange='', routing_key='notionwriter', body=json.dumps(data))
		case 'companiesapi':
			logging.info("Sending queue message to companiesapi")
			channel.queue_declare(queue='companiesapi')
			channel.basic_publish(exchange='', routing_key='companiesapi', body=json.dumps(companydata))