#!/bin/bash

# selenium
python3 scraper.py selenium

# GPT
python3 scraper.py gpt &

# notionwriter
python3 scraper.py notionwriter &

# companiesapi
python3 scraper.py companiesapi &

# companieswriter
python3 scraper.py companieswriter &

# notionloader and companiesloader
crond -f