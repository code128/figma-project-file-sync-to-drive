#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
from googleapiclient.discovery import build
import pprint
import sys
import requests
import json
import os

from flask import Flask, make_response, jsonify
app = Flask(__name__)


# Global variables
figma_token = os.environ.get('figma_token')
figma_team = os.environ.get('figma_team')
team_name = ""
project_name_list = []
projects_and_files = []
headers = None


def setHeaders():
    global headers
    headers = {
        'Accept': "*/*",
        'Cache-Control': "no-cache",
        'Host': "api.figma.com",
        'accept-encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
    }
    headers["X-FIGMA-TOKEN"] = figma_token


def getTeamAndProjects():
    global team_name
    global project_name_list
    url = "https://api.figma.com/v1/teams/" + figma_team + "/projects"
    response = requests.request("GET", url, headers=headers)
    respJson = response.json()
    team_name = respJson["name"]
    project_name_list = respJson["projects"]


def getProjectFiles():
    global projects_and_files
    for project in project_name_list:
        url = "https://api.figma.com/v1/projects/" + project["id"] + "/files"
        response = requests.request("GET", url, headers=headers)
        projects_and_files.append(response.json())


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
# The ID of a sample document.
DOCUMENT_ID = '1vGIk9uDHd3KP7Yb2b0r_SNH9h3ZJQDlydVxI1KUQ9u8'


def testServiceAccount():
    service = build('docs', 'v1')
    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    print('The title of the document is: {}'.format(document.get('title')))


@app.route('/')
def main():
    testServiceAccount()
    data = {'message': 'Created', 'code': 'SUCCESS'}
    return make_response(jsonify(data), 201)
    # setHeaders()
    # getTeamAndProjects()
    # getProjectFiles()
    # pp = pprint.PrettyPrinter(indent=4, width=80, compact=False)
    # # pp.pprint(projects_and_files)
    # # print(json.dumps(projects_and_files))
    # return json.dumps(projects_and_files)


# Main body
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
