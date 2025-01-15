from notion import Notion
import logging
from dotenv import load_dotenv
import os
from notifications import Notifications
import json
import pika

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s: %(message)s', level=logging.INFO)

class CompaniesWriter:
	def __init__(self, args):
		logging.info("Setting up")
		load_dotenv()
		self.n = Notifications()
		self.notion = Notion()
		self.inputfolder = args.inputfolder

	def publish(self, filename):
		os.rename(f"{self.inputfolder}/{filename}", f"{self.inputfolder}/DONE-{filename}")

	def update_company(self,data):
		logging.info("Updating company %s" % data["name"])
		self.notion.update_company(data)

	def run(self):
		logging.info("Running CompaniesWriter.")
		count = 0
		folder_path = self.inputfolder
		for filename in os.listdir(folder_path):
			if filename.endswith('.json') and not filename.startswith("DONE") and filename.startswith("enrich-"):
				logging.info("Loaded file")
				with open(f"{folder_path}/{filename}", 'r') as f:
					companydata = json.loads(f.read())
				notion_id = filename.replace("enrich-",'').replace('.json','')
				companydata['notion_id'] = notion_id
				logging.info(f"Loaded data for company id {notion_id} (filename: {filename})")
				try:
					self.update_company(companydata)
				except:
					raise
					self.n.error(f"Something went wrong saving company {notion_id} to notion")
					exit()
				
				self.publish(filename)
				count+=1
		if count:
			self.n.info(f"Saved {count} companies back to notion")


	def loop(self):
		self.run()