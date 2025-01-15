import argparse
import logging
from notifications import Notifications
from companiesenrich import CompaniesEnrich
from companiesloader import CompaniesLoader
from companieswriter import CompaniesWriter
import traceback

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s: %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["companiesenrich", "companiesloader", "companieswriter"])
parser.add_argument("-o", "--outputfolder", help="Folder to save output to", required=False, default="workspace")
parser.add_argument("-i", "--inputfolder", help="Folder to get input from", required=False, default="workspace")
args = parser.parse_args()

if __name__ == "__main__":
    match args.mode:
        case 'companiesenrich':
            logging.info("Companies Enrichment Mode")
            runner = CompaniesEnrich(args)
        case 'companiesloader':
            logging.info("Companies Loader Mode")
            runner = CompaniesLoader(args)
        case 'companieswriter':
            logging.info("Companies Writer Mode")
            runner = CompaniesWriter(args)
    n = Notifications()
    try:
        runner.loop()
    except Exception as e:
        traceback.print_exc()
        n.critical("Runner crashed: %s" % runner)
