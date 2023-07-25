# jira-api
A class to manage connectivity with Jira.

# Useful References

* Cookie-based authentication is deprecated
  + https://developer.atlassian.com/cloud/jira/platform/jira-rest-api-cookie-based-authentication/

* How to create the Jira Token for Basic Authentication
  + https://community.atlassian.com/t5/Jira-questions/How-to-authenticate-to-Jira-REST-API-with-curl/qaq-p/1312165
  + tldr: `echo -n EMAIL:API_TOKEN | base64`

* How to create the SonarQube Token for Basic Authentication
  + `echo -n API_TOKEN | base64`