#!/usr/bin/env python3

import requests
import json
import sys
import os


class JiraAPI(object):

    def __init__(self):

        self.jira_url = os.getenv("JIRA_URL")
        self.jira_token = os.getenv("ENCODED_JIRA_TOKEN")
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {self.jira_token}',
        }

        if self.jira_url is None:
            raise Exception("JIRA_URL is not set.")
            sys.exit(12)
        if self.jira_token is None:
            raise Exception("JIRA_ENCODED_TOKEN is not set.")
            sys.exit(13)

    def __del__(self):
        pass

    def ticket_already_exists(self, project_key, unique_term):

        url = self.jira_url + "/rest/api/3/search"

        jql = f"project = {project_key} AND description ~ \"{unique_term}\""

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

        if len(response.json()["issues"]) == 0:
            return False
        else:
            return True

    def get_issues(self, project_key, unique_desc = ""):
        
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
            print(f"Failed to create Jira ticket. Status code: {response.status_code}")
            return None

    def close_issue(self, issue_key):

        # Note: The id for the 'Close' transition can vary
        transition_payload = {'transition': {'id': '31'}}
        response = requests.post(
            f'{self.jira_url}/rest/api/3/issue/{issue_key}/transitions', 
            headers = self.headers, 
            data = json.dumps(transition_payload))
        response.raise_for_status()

    def add_comment(self, issue_key, comment):

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
        response = requests.post(
            f'{self.jira_url}/rest/api/3/issue/{issue_key}/comment',
            headers = self.headers, 
            data = json.dumps(payload))
        response.raise_for_status()

    def reopen_issue(self, issue_key):

        # Note: The id for the 'Open' transition can vary
        transition_payload = {'transition': {'id': '11'}}
        response = requests.post(
            f'{self.jira_url}/rest/api/3/issue/{issue_key}/transitions',
            headers = self.headers, 
            data = json.dumps(transition_payload))
        response.raise_for_status()


if __name__ == '__main__':
    jira = JiraAPI()

