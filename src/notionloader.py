from notion import Notion
import logging
from dotenv import load_dotenv
import os
from notifications import Notifications
import time


class NotionLoader:
	def __init__(self):
		logging.info("Setting up")
		load_dotenv()
		self.n = Notifications()

	def load_from_notion(self):
		logging.info("Start loading from notion")
		n = Notion()
		followers = n.load_users_to_scrape()
		with open("%s/0_to_scrape.txt" % os.environ['WORKSPACE'], 'w') as file:
			for f in followers:
				logging.debug(f)
				file.write("%s:%s\n" % (f["id"], f["properties"]["URL"]["url"]))
		return followers
	
	def run(self):
		self.load_from_notion()
		
	def loop(self):
		try:
			self.run()
			logging.info("Going to sleep...")
			time.sleep(60*60*24)
		except Exception as e:
			self.n.critical("NotionLoader crashed: %s" % e)
