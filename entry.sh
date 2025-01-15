#!/bin/bash

# companiesapi
python3 scraper.py companiesapi &

# companieswriter
python3 scraper.py companieswriter &

# notionloader and companiesloader
crond -f