import argparse
import logging
from headlessbrowser import HeadlessBrowser
from gpt import GPTRunner
from notionloader import NotionLoader
from notionwriter import NotionWriter
from notifications import Notifications
from companiesapi import CompaniesAPI
from companiesloader import CompaniesLoader
from companieswriter import CompaniesWriter
import traceback

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s: %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["notionloader", "selenium", "gpt", "notionwriter", "companiesapi", "companiesloader", "companieswriter"])
args = parser.parse_args()

if __name__ == "__main__":
    match args.mode:
        case 'selenium':
            logging.info("Starting Selenium Mode")
            runner = HeadlessBrowser()
        case 'notionwriter':
            logging.info("Starting Write back to notion")
            runner = NotionWriter()
        case 'gpt':
            logging.info("Starting GPT")
            runner = GPTRunner()
        case 'notionloader':
            logging.info("Loading from Notion")
            runner = NotionLoader()
        case 'companiesapi':
            logging.info("Companies API Mode")
            runner = CompaniesAPI()
        case 'companiesloader':
            logging.info("Companies Loader Mode")
            runner = CompaniesLoader()
        case 'companieswriter':
            logging.info("Companies Writer Mode")
            runner = CompaniesWriter()
    n = Notifications()
    try:
        runner.loop()
    except Exception as e:
        traceback.print_exc()
        # n.critical("Runner crashed: %s" % runner)
