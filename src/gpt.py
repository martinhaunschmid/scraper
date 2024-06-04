from openai import OpenAI
import json
import os
import logging
from dotenv import load_dotenv
import pika
# import httpx
from notifications import Notifications
from openai import RateLimitError


prompt = """
Ich habe die folgenden Infos über eine Person

%%PROFILE%%

Sieh dir die Infos an und erstelle ein JSON objekt mit den folgenden keys:
name
description
followers
services (= nur Text)
information (= der Inhalt des Info Blocks)
experience (das Folgende bitte für jede einzelne Stelle im Profil)
- workplace
- job_title
- job_since_when
- url (=the URL of the company, if you find it, Null if you don't find it)
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
				model = "gpt-4-turbo-preview",
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
			result = self.call_chatgpt(data['profile_text'])
			
			print(result)
			with open("%s/%s.json" % (os.environ.get("WORKSPACE"), data['slug']), 'w') as f:
				f.write(json.dumps(result))

			data['scraped'] = result
			self.publish(data)
			ch.basic_ack(delivery_tag = method.delivery_tag)
		except Exception as e:
			self.n.critical("GPT crashed: %s" % e)
			pass

	def loop(self):
		logging.info("Start consuming...")
		self.channel.basic_consume(queue='gpt', on_message_callback=self.run, auto_ack=False)
		logging.info("Waiting for messages")
		self.channel.start_consuming()
