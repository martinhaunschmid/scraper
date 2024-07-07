from notion import Notion
from dotenv import load_dotenv
from notifications import Notifications
import os
import logging

directory = '/Users/ntrm/Downloads/'
prefix = 'ntrm-linkedin-automation-'

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s: %(message)s', level=logging.INFO)

if __name__ == "__main__":
    logging.info("This is used for pushing manually scraped .txt profiles to notion")

    notion = Notion()

    # first, open up all the files to push to notion
    for filename in os.listdir(directory):
        if filename.startswith(prefix) and filename.endswith('.txt'):
            filecontent = ""
            with open("%s%s" % (directory, filename),'r') as f:
                filecontent = f.read()
            person = filename.replace(prefix,"").replace(".txt","")
            logging.info("Searching for %s in notion" % person)
            notion_id = notion.id_for_follower_by_name(person)
            if not notion_id:
                logging.error("Didn't find %s" % person)
            logging.info("-> Notion id: %s" % notion_id)
            notion.set_profile_text(notion_id, filecontent)

