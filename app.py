#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
import pprint
import sys
import requests
import json
import os

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


def main():
    setHeaders()
    getTeamAndProjects()
    getProjectFiles()
    pp = pprint.PrettyPrinter(indent=4, width=80, compact=False)
    # pp.pprint(projects_and_files)
    print(json.dumps(projects_and_files))
    return json.dumps(projects_and_files)


# Main body
if __name__ == '__main__':
    main()
