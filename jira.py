#!/usr/bin/env python3

import requests
import json
import sys
import os


class JiraAPI(object):

    # Initialize from environment variables
    def __init__(self):

        # Cloud URL
        self.jira_url = os.getenv("JIRA_URL")
        # Encoded token, `email:api_token` as base64
        self.jira_token = os.getenv("ENCODED_JIRA_TOKEN")
        # Reusable headers
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.jira_token}',
        }

        # Check if the environment variables are set, abort otherwise
        if self.jira_url is None:
            raise Exception("JIRA_URL is not set.")
            sys.exit(12)
        if self.jira_token is None:
            raise Exception("JIRA_ENCODED_TOKEN is not set.")
            sys.exit(13)

    # Do something someday with deleted object cleanup
    def __del__(self):
        pass

    # Check if a given issue already exists based on a unique search term
    def check_if_issue_already_exists(self, project_key, unique_desc):

        url = self.jira_url + "/rest/api/3/search"
        # Search for the issue based on the unique search term
        jql = f"project = {project_key} AND description ~ \"{unique_desc}\""
        payload = {
            'jql': jql,
            'fields': ['key', 'summary', 'description']
        }

        response = requests.post(
            url,
            headers = self.headers,
            data = json.dumps(payload),
        )

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        # If the issue doesn't exist, 
        if len(response.json()["issues"]) == 0:
            return False
        # Else issue exists
        else:
            return True

    # Get the issue key based on a unique search term, or all issues
    def get_issues(self, project_key, unique_desc = ""):

        # Search based on a unique description or just project        
        if unique_desc == "":
            jql = f"project = {project_key}"
        else:
            jql = f"project = {project_key} AND description ~ \"{unique_desc}\""
        payload = {'jql': jql}
        response = requests.post(f"{self.jira_url}/rest/api/3/search", 
                                 headers = self.headers, 
                                 data = json.dumps(payload))
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        issues = response.json()['issues']
        return issues

    # Create a new issue in a project, with subject, description, and type
    def create_issue(self, project_key, summary, description, issue_type):

        url = self.jira_url + "/rest/api/2/issue"

        data = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "summary": summary,
                "description": description,
                "issuetype": {
                    "name": issue_type
                }
            }
        }

        response = requests.post(url, json = data, headers = self.headers)

        # Raise an exception if the request was unsuccessful
        response.raise_for_status()

        if response.status_code == 201:
            return response.json()["key"]
        else:
            print(f"Failed to create Jira issue. Status code: {response.status_code}")
            return None

    # Close an open Jira issue
    def close_issue(self, issue_key):

        # Note: The id for the 'Close' transition can vary
        transition_payload = {'transition': {'id': '31'}}
        response = requests.post(
            f'{self.jira_url}/rest/api/3/issue/{issue_key}/transitions', 
            headers = self.headers, 
            data = json.dumps(transition_payload))
        response.raise_for_status()
        return True

    # Transition a Jira issue into In-Progress (assumed id:21)
    def set_issue_in_progress(self, issue_key):

        # Note: The id for the 'In Progress' transition can vary
        transition_payload = {'transition': {'id': '21'}}
        response = requests.post(
            f'{self.jira_url}/rest/api/3/issue/{issue_key}/transitions', 
            headers = self.headers, 
            data = json.dumps(transition_payload))
        response.raise_for_status()
        return True

    def add_comment_to_issue(self, issue_key, comment):

        # The payload for adding a comment
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": comment,
                                "type": "text"
                            }
                        ]
                    }
                ]
            }
        }
        # Add the comment
        response = requests.post(
            f'{self.jira_url}/rest/api/3/issue/{issue_key}/comment',
            headers = self.headers, 
            data = json.dumps(payload))
        response.raise_for_status()
        return True

    def reopen_closed_issue(self, issue_key):

        # Note: The id for the 'Open' transition can vary
        transition_payload = {'transition': {'id': '11'}}
        response = requests.post(
            f'{self.jira_url}/rest/api/3/issue/{issue_key}/transitions',
            headers = self.headers, 
            data = json.dumps(transition_payload))
        response.raise_for_status()
        return True


if __name__ == '__main__':
    jira = JiraAPI()

