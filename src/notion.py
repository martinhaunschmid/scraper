import os
from notion_client import Client, APIErrorCode, APIResponseError
from notion_client.helpers import collect_paginated_api
from dotenv import load_dotenv
import logging
import traceback
import json
from notifications import Notifications

class Notion:
	client = None
	databaseId = None

	def __init__(self):
		logging.info("Initializing Notion")
		load_dotenv()
		self.client = Client(auth=os.environ["NOTION_SECRET"])
		self.databaseId = os.environ["NOTION_FOLLOWERS_DATABASE_ID"]
		self.companyDatabaseId = os.environ["NOTION_COMPANIES_DATABASE_ID"]
		self.n = Notifications()

	def id_for_company_by_name(self, companyname):
		logging.info("Loading company %s" % companyname)
		try:
			company = self.client.databases.query(
				**{
					"database_id": self.companyDatabaseId,
					"page_size": 1,
					"filter": {
						"property":"Name",
						"rich_text":{
							"equals": companyname
						}
					}
				}
			)

			if len(company['results']) == 1:
				return company['results'][0]['id']
			else:
				return None
		except APIResponseError as e:
			self.n.critical("Something went wrong with the notion api %s" % e)

	def write_company_to_database(self,companydata):
		logging.info("Writing Company %s back to Notion" % companydata['name'])
		company = self.id_for_company_by_name(companydata['name'])
		if company is None:
			logging.info("Creating the company")
			try:
				result = self.client.pages.create(
					**{
						"parent":{
							"database_id": self.companyDatabaseId,
						},
						"properties":{
							"Name": {
								"title": [
									{
										"text": {
			 								"content": companydata['name']
			  							}
			  						}
			  					],
							},
							"URL": {
								"url":companydata['url']
							}
						}
					}
				)
				return result['id']
			except APIResponseError as e:
				traceback.print_exc(e)
				self.n.critical("Could not create Company %s" % companydata['name'])
		return company
	
	def load_companies_to_enrich(self):
		logging.info("Loading Companies to scrape")
		try:
			companies = self.client.databases.query(
				**{
				"database_id": self.companyDatabaseId,
				"page_size": 100,
				"filter": {
					"property":"Scrape",
					"status":{
						"equals":"Not Started"
					}
				}
				})
			logging.info("Found %s companies for now" % len(companies["results"]))
			return companies["results"]
		except APIResponseError as error:
			logging.critical("Something went wrong with the Notion API")

	def set_company_to_problem(self,notion_id):
		logging.info("Setting company %s to problematic" % notion_id)
		try:
			company = self.client.pages.update(
				**{
					"page_id": notion_id,
					"properties":{
						"Scrape": {
							"status":{
								"name": "Problem"
							}
						}
					}
				}
			)
		except APIResponseError as error:
			traceback.print_exc(error)
			self.n.critical("Something went wrong with the Notion API when writing Person")
	
	def build_properties(self, data):
		# Builds a string for usage in the notes of a person
		scraped = data['scraped']
		company_names = []
		job_string = ""
		for c in scraped['experience']:
			if "Heute" in c['job_since_when']:
				company_names.append({"name":c['workplace']})
				job_string += "%s: %s\n" % (c['workplace'], c['job_title'])
		return [company_names, job_string.strip()]

	def load_users_to_scrape(self):
		logging.info("Loading Users to scrape")
		try:
			followers = self.client.databases.query(
				**{
				"database_id": self.databaseId,
				"page_size": 100,
				"filter": {
					"property":"Unternehmen",
					"url":{
						"is_empty": True
					}
				}
				})
			logging.info("Found %s followers for now" % len(followers["results"]))
			return followers["results"]
		except APIResponseError as error:
			logging.critical("Something went wrong with the Notion API")

	def update_follower(self, data):
		logging.info("Writing Info back to User %s" % data['notion_id'])
		# We're updating the following fields
		# - √ Unternehmen (Multi Select)
		# - √ URL: the new, non-cloaked linkedin profile URL
		# - √ Notes: The user's info box
		# - √ Beschreibung: The user's description
		# - √ Role: A concatenated string of the current positions
		# - √ Companies: Relations to Companies database
		scraped = data['scraped']
		[company_names, job_string] = self.build_properties(data)
		try:
			person = self.client.pages.update(
				**{
					"page_id": data['notion_id'],
					"properties":{
						"URL": {
							"url": data['profile_url']
						},
						"Role":{
							"rich_text": [{
								"text": {"content":job_string}
							}]
						},
						"Unternehmen": {
							"multi_select": company_names
						},
						"Notes": {
							"rich_text":[{"text":{"content":scraped['information']}}]
						},
						"Beschreibung": {
							"rich_text":[{"text":{"content":scraped['description']}}]
						},
						"Companies": {
							"relation": data['companies']
						} 
					}
				}
			)
			print(person)
		except APIResponseError as error:
			traceback.print_exc(error)
			self.n.critical("Something went wrong with the Notion API when writing Person")