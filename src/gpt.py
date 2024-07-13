from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
import pika
import random
# import httpx
import traceback
from notifications import Notifications
from openai import RateLimitError


prompt = """
Ich habe die folgenden Infos über eine Person

%%PROFILE%%

Sieh dir die Infos an vervollständige folgendes JSON Objekt:

{
	"name":"TODO",
	"description": "TODO"
	"followers": TODO,
	"services": "TODO",
	"information": "TODO",
	"experience": [  // Hier für jede einzelne Stelle im Profil ein JSON Object einfügen
		{
			"workplace":"TODO",
			"job_title":"TODO",
			"job_since_when": "TODO"
			"url": "TODO"
		}
	]
}

Gib als Antwort nur das JSON Objekt.
"""

class GPTRunner:

	def __init__(self):
		logging.info("Setting up")
		load_dotenv()

		# for debugging: http_client=httpx.Client(proxy="http://127.0.0.1:8080", verify=False)
		self.client = OpenAI(api_key=os.environ.get("OPENAI_KEY"))
		self.n = Notifications()
		self.setup_queue()

	def setup_queue(self):
		self.queue = pika.BlockingConnection(pika.ConnectionParameters(host=os.environ.get("QUEUE_HOST"), port=os.environ.get("QUEUE_PORT")))
		self.channel = self.queue.channel()
		self.channel.queue_declare(queue="gpt")

	def teardown_queue(self):
		self.queue.close()		

	def call_chatgpt(self, profile_text):
		logging.info("Calling GPT-4")
		try:
			res = self.client.chat.completions.create(
				model = "gpt-4o",
				messages=[{"role": "user","content": prompt.replace('%%PROFILE%%', profile_text)}])
		except RateLimitError as e:
			logging.warning("Hit ratelimit")
			self.n.warn("GPT Ratelimit hit!")
			print(json.dumps(e))
		answer = res.choices[0].message.content.strip()
		json_doc = ""
		for line in answer.split("\n"):
			
			if not "```" in line:
				json_doc += line
		with open("%s/%s-openai.json" % (os.environ.get("WORKSPACE"), random.randint(1,1000)), 'w') as f:
				f.write(json_doc)
		return json.loads(json_doc)
	
	def publish(self,data):
		logging.info("Publishing data to write back to notion for %s" % data['slug'])
		# Writes to queue
		self.channel.queue_declare(queue='notionwriter')
		self.channel.basic_publish(exchange='', routing_key='notionwriter', body=json.dumps(data))
	
	def run(self, ch, method, properties,body):
		logging.info("Received Message from Queue")
		data = json.loads(body)
		logging.info("Analyzing %s" % data['slug'])
		
		try:
			result = self.call_chatgpt(data['profiletext'])
		
			data['scraped'] = result
			self.publish(data)
			ch.basic_ack(delivery_tag = method.delivery_tag)
		except Exception as e:
			traceback.print_exc()
			self.n.critical("GPT crashed: %s" % e)
			pass

	def loop(self):
		logging.info("Start consuming...")
		self.channel.basic_consume(queue='gpt', on_message_callback=self.run, auto_ack=False)
		logging.info("Waiting for messages")
		self.channel.start_consuming()
