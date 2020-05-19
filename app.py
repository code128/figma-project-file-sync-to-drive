#!/user/bin/env python3 -tt
"""
Module documentation.
"""

# Imports
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pprint
import sys
import requests
import json
import os
import arrow

from flask import Flask, make_response, jsonify, render_template
app = Flask(__name__)


@app.template_filter()
def friendly_time(value):
    return arrow.get(value).humanize()


# Global variables
figma_token = os.environ.get('figma_token')
figma_team = os.environ.get('figma_team')
google_drive_folder_id = os.environ.get('google_drive_folder_id')
created_file_name = os.environ.get('created_file_name')
team_name = ""
headers = None
drive = build('drive', 'v3')


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
    url = "https://api.figma.com/v1/teams/" + figma_team + "/projects"
    response = requests.request("GET", url, headers=headers)
    respJson = response.json()
    team_name = respJson["name"]
    project_list = respJson["projects"]
    return (team_name, project_list)


def getProjectFiles(project_list):
    projects_and_files = []
    for project in project_list:
        url = "https://api.figma.com/v1/projects/" + project["id"] + "/files"
        response = requests.request("GET", url, headers=headers)
        projects_and_files.append(response.json())
    return projects_and_files


def uploadToGoogleDrive(localFile):
    file_metadata = {
        'name': localFile,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [google_drive_folder_id]
    }
    media = MediaFileUpload(localFile,
                            mimetype='text/html',
                            resumable=True)
    file = drive.files().create(body=file_metadata,
                                media_body=media,
                                fields='id').execute()
    print('File ID: %s' % file.get('id'))


def createLocalHTMLFile(figmaJSON):
    f = open(created_file_name, "w+")
    f.write(render_template("export.html", team_name=team_name, result=figmaJSON))
    f.close()
    return created_file_name


def deleteExistingFile():
    # Search for any existing files with the same name and delete them
    page_token = None
    query = "name contains '" + created_file_name + "'"
    while True:
        response = drive.files().list(q=query,
                                      spaces='drive',
                                      fields='nextPageToken, files(id, name)',
                                      pageToken=page_token).execute()
        print(response)
        for file in response.get('files', []):
            print('Found file: %s (%s)' % (file.get('name'), file.get('id')))
            # Process change
            dresp = drive.files().delete(fileId=file["id"]).execute()
            print(dresp)

        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break


@ app.route('/')
def main():
    global team_name
    setHeaders()
    team_name, project_list = getTeamAndProjects()
    projects_and_files = getProjectFiles(project_list)
    localFile = createLocalHTMLFile(projects_and_files)
    deleteExistingFile()
    uploadToGoogleDrive(localFile)
    return make_response(jsonify(projects_and_files), 201)


# Main body
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
