#!/usr/bin/env python3

import requests
import json
import sys
import os


class ConfluenceAPI(object):

    # Initialize from environment variables
    def __init__(self):

        # Cloud URL
        self.confluence_url = os.getenv("CONFLUENCE_URL")
        # Encoded token, `email:api_token` as base64
        self.confluence_token = os.getenv("ENCODED_CONFLUENCE_TOKEN")
        # Reusable headers
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.confluence_token}',
        }

        # Check if the environment variables are set, abort otherwise
        if self.confluence_url is None:
            raise Exception("JIRA_URL is not set.")
            sys.exit(12)
        if self.confluence_token is None:
            raise Exception("JIRA_ENCODED_TOKEN is not set.")
            sys.exit(13)

    # Do something someday with deleted object cleanup
    def __del__(self):
        pass

    def create_page(self, space_key, title, content):

        # Define your new page data
        new_page = {
            'type': 'page',
            'title': title,
            'space': {
                'key': space_key
            },
            'body': {
                'storage': {
                    'value': content,
                    'representation': 'storage'
                }
            }
        }

        response = requests.post(
            f'{self.confluence_url}/rest/api/content',
            headers = self.headers,
            data = json.dumps(new_page)
        )

        response.raise_for_status()  

        # Parse and print the JSON response from Confluence
        page_data = response.json()
        print(json.dumps(page_data, indent = 4))

        # Return the page ID
        return page_data['id']

    def update_page(self, page_id, title, content):
            
        # Define your updated page data
        updated_page = {
            'type': 'page',
            'title': title,
            'body': {
                'storage': {
                    'value': content,
                    'representation': 'storage'
                }
            },
            'version': {
                'number': 2
            }
        }

        response = requests.put(
            f'{self.confluence_url}/rest/api/content/{page_id}',
            headers = self.headers,
            data = json.dumps(updated_page)
        )

        response.raise_for_status()

        page_data = response.json()
        print(json.dumps(page_data, indent = 4))

    def get_pages(self, title, space_key = ""):

        if space_key != "":
            cql = f'title = "{title}" and space.key = "{space_key}"'
        else:
            cql = f'title = "{title}"'

        # Send a GET request to the search API
        response = requests.get(
            f'{self.confluence_url}/rest/api/content/search?cql={cql}',
            headers = self.headers,
        )

        response.raise_for_status()

        # Parse and print the JSON response from Confluence
        search_results = response.json()
        print(json.dumps(search_results, indent = 4))
        return search_results['results']
    
    def upload_attachment(self, page_id, file_path):

        self.headers['X-Atlassian-Token'] = 'no-check'

        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Set the data payload of the request to the binary content of the file
            files = {'file': file}

            # Send a POST request to the 'Create attachment' endpoint
            response = requests.post(
                f'{self.confluence_url}/rest/api/content/{page_id}/child/attachment',
                headers = self.headers,
                files = files
            )

        response.raise_for_status()

        # Parse and print the JSON response from Confluence
        attachment_data = response.json()
        print(json.dumps(attachment_data, indent = 4))