from notion import Notion
import logging
from dotenv import load_dotenv
from notifications import Notifications
import traceback
import os
import json


class CompaniesLoader:
	def __init__(self, args):
		logging.info("Setting up")
		load_dotenv()
		self.n = Notifications()
		self.outputfolder = args.outputfolder if args and args.outputfolder else None

	def publish(self, companies):
		if not self.outputfolder:
			logging.info(f"Not saving anything, no outputfolder set")
			return
		
		with open(f"{self.outputfolder}/companiesloader.json", 'wb') as f:
			f.write(json.dumps(companies, ensure_ascii=False).encode('utf-8'))

	def load_from_notion(self):
		logging.info("Start loading from notion")
		n = Notion()
		companies = n.load_companies_to_enrich()

		# build objects for message queue
		publish = []
		for c in companies:
			msg = {
				"name": c["properties"]["Name"]["title"][0]["text"]["content"],
				"url": c["properties"]["URL"]["url"],
				"notion_id": c["id"]
			}
			publish.append(msg)
		self.publish(publish)
	
	def run(self):
		self.load_from_notion()
		
	def loop(self):
		try:
			self.run()
			logging.info("Going to sleep...")
		except Exception as e:
			self.n.critical("CompaniesLoader crashed: %s" % e)
