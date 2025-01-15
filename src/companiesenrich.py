import json
from dotenv import load_dotenv
from notifications import Notifications
import os
import logging
import subprocess
import time

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s: %(message)s', level=logging.INFO)

PROMPT="""Can you fill in the details of the company "COMPANYNAME" in the following json and return it without any additional text:

```
{
"name":"COMPANYNAME",
"url":"TODO",
"description":"TODO",
"industry":"TODO",
"subindustry": "TODO",
"city":"TODO",
"country":"TODO",
"employees":"TODO",
"income":"TODO"
}
```
Do not return any additional information about the company besides the JSON file.
"""

class CompaniesEnrich:
    def __init__(self, args):
        logging.info("Setting up")
        load_dotenv()
        self.n = Notifications()
        self.outputfolder = args.outputfolder
        self.inputfolder = args.inputfolder

    def poll_clipboard(self, canary="TODO"):
        # polls clipboard until canary is not there anymore
        while True:
            try:
                #Tell the IO system to decode IPC IO with utf-8,
                #to prevent UnicodeDecodeErrors on python3
                os.environ['LANG'] = 'en_US.utf-8'
                contents = subprocess.Popen(
                    ['pbpaste'], stdout=subprocess.PIPE).communicate()[0].decode('utf-8')
                if not canary in contents:
                    return contents
            except OSError as why:
                raise XcodeNotFound
            time.sleep(1)
    
    def send_to_clipboard(self,text):
        try:
            subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE).communicate(
                    text.encode("utf-8"))
        except OSError as why:
            raise XcodeNotFound

    def publish(self, company, text):
        with open(f"{self.outputfolder}/enrich-{company['notion_id']}.json", 'wb') as f:
            f.write(text.encode("utf-8"))

    def run(self):
        with open(f"{self.inputfolder}/companiesloader.json", 'r') as f:
            companies = json.loads(f.read())

        amount = len(companies)
        count = 0
        logging.info(f"Going through {amount} companies")
        for c in companies:
            count+=1
            # build the "Prompt to display to the user"
            if os.path.isfile(f"{self.outputfolder}/enrich-{c['notion_id']}.json"):
                logging.info("File exists, skipping.")
                continue

            logging.info(f"Building prompt for {c['name']}")
            clip = PROMPT.replace("COMPANYNAME", c['name'])
            self.send_to_clipboard(clip)

            # then wait for the result
            result = self.poll_clipboard()
            # print(result)
            self.publish(c, result)
            count+=1
            logging.info(f"{count}/{amount} done.")
        self.n.info(f"Enriched {count} companies via manual OpenAI shenanigans")

    def loop(self):
        self.run()