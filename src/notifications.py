from dotenv import load_dotenv
import os
import logging
import requests

class Notifications:
    def __init__(self):
        self.webhook = os.environ.get("WEBHOOK")

    def info(self, text):
        emoji = "ℹ️"
        logging.info("%s %s" % (emoji, text))
        self.notify(emoji, text)

    def warn(self,text):
        emoji = "⚠️"
        logging.warn("%s %s" % (emoji, text))
        self.notify(emoji,text)
    
    def error(self, text):
        emoji = "💥"
        logging.error("%s %s" % (emoji, text))
        self.notify(emoji, text)

    def critical(self, text):
        emoji = "💥"
        logging.critical("%s %s" % (emoji, text))
        self.notify(emoji, text)

    def notify(self, emoji, text):
        requests.post(self.webhook, json={"text": "%s %s" % (emoji,text)})
