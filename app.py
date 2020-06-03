# Imports
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pprint
import sys
import requests
import json
import os
import arrow
import re

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
headers = {
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Host': "api.figma.com",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
}
headers["X-FIGMA-TOKEN"] = figma_token
service = build('sheets', 'v4')
plugin_id = '749778475482705952'
spreadsheet_id = '1m4T72la8TcogXLECMGspXJkeWfPv0YxJ9-eJlGagLjs'
google_slide_deck_prefix = 'https://docs.google.com/presentation/d/'


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


def getFigmaFileInformation(file_id):
    url = "https://api.figma.com/v1/files/" + file_id + "/versions"
    response = requests.request("GET", url, headers=headers)
    respJson = response.json()
    return respJson


def getFigmaFileSlideDeck(file_id):
    url = "https://api.figma.com/v1/files/" + \
        file_id + "?depth=1&plugin_data=" + plugin_id
    response = requests.request("GET", url, headers=headers)
    respJson = response.json()
    try:
        slideDeckID = respJson["document"]["pluginData"][plugin_id]["presentationId"]
        return google_slide_deck_prefix + slideDeckID
    except:
        return ""


def updateFilesWithDeeperData(projects_and_files):
    # for each file get the figamFileInfo
    for project in projects_and_files:
        for file in project["files"]:
            file["fileInfo"] = getFigmaFileInformation(file["key"])
            file["relatedSlideDeck"] = getFigmaFileSlideDeck(file["key"])


def updateGoogleSheet(projects_and_files):
    # Get a connection to the correct google sheet
    # Go row by row looking for the files file["key’
    # If it exists update it with the latest info from here (Tags, Users, Version Info, Version Count)
    rangeCounter = 1
    for project in projects_and_files:
        for file_info in project["files"]:
            rangeCounter += 1
            range_name = str(rangeCounter) + ":" + str(rangeCounter)
            body = {
                'values': [figmaFileInfoToSheetStyle(file_info, project)]
            }
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption="USER_ENTERED", body=body).execute()
            print('{0} cells updated.'.format(result.get('updatedCells')))


def getTags(description):
    # parse out all the #'s for tags and return them
    matches = []
    if description:
        regex = r"#\w+"
        matches = re.findall(regex, description, re.MULTILINE)
    return matches


def figmaFileInfoToSheetStyle(file_data, project_data):
    # figmaFileInfo looks like this:
    # { "key": "RwLRoiiage5tSarrPayful",
    #   "name": "Apps on CR Concepts",
    # "thumbnail_url": "https://s3-alpha-sig.figma.com/thumbnails/4c3c4d42-50fd-4f21-b6fa-9fe041a517ca?Expires=1591574400&Signature=dxKSU9zP5hATCJvfFNWyTy8f-1qz41F6BYlUjA-jcINRSM-jJiJUtB1OemCzKyRBWfN85CgJhg0GucVpeJfhcc~x~VEIpqqn-kgGdzE4t3yqgmIeOipuZb75owldyxegqxO5Q2QdPdT0DrYgsrEdI13eD8OV-MM-LiWQqjIwkp7pIEba86~~6oIKDRT-lUJl59oyZT-FLpncWdReMgNj6gUdE~pkxTLrGBSqZmH3ULkLamzrQ2HgxNh4oM2n3uhjXsCTdeSAYvefuqWt8-qYb7WpatxgYOEvccMvSU97FLzfLwjHQHyedry7BOR7Lw0YhDdRHWsZpFB-wRwY6Hxymg__&Key-Pair-Id=APKAINTVSUGEWH5XD5UA",
    # "last_modified": "2020-04-27T22:00:44Z",
    # "fileInfo": {
    # 	"versions": [
    # 		{
    # 		"id": "309890308",
    # 		"created_at": "2020-04-27T22:00:15Z",
    # 		"label": "Version Testing",
    #		"description": "Adding something to the description. #one @two",
    #		"user": {
    #				"handle": "Joe Giovenco",
    #				"img_url": "https://s3-alpha.figma.com/profile/e9bd6005-6ec5-4134-af83-af16aae402b1",
    #				"id": "767119165052046715"
    #			},
    # 		"thumbnail_url": "https://s3-alpha-sig.figma.com/thumbnails/4c3c4d42-50fd-4f21-b6fa-9fe041a517ca?Expires=1591574400&Signature=dxKSU9zP5hATCJvfFNWyTy8f-1qz41F6BYlUjA-jcINRSM-jJiJUtB1OemCzKyRBWfN85CgJhg0GucVpeJfhcc~x~VEIpqqn-kgGdzE4t3yqgmIeOipuZb75owldyxegqxO5Q2QdPdT0DrYgsrEdI13eD8OV-MM-LiWQqjIwkp7pIEba86~~6oIKDRT-lUJl59oyZT-FLpncWdReMgNj6gUdE~pkxTLrGBSqZmH3ULkLamzrQ2HgxNh4oM2n3uhjXsCTdeSAYvefuqWt8-qYb7WpatxgYOEvccMvSU97FLzfLwjHQHyedry7BOR7Lw0YhDdRHWsZpFB-wRwY6Hxymg__&Key-Pair-Id=APKAINTVSUGEWH5XD5UA"
    # 		}
    versions = file_data["fileInfo"]["versions"]
    lastUser = versions[0]["user"]["handle"]
    lastUserImg = versions[0]["user"]["img_url"]
    label = versions[0]["label"]
    description = versions[0]["description"]
    tags = getTags(description)

    versionCount = len(versions)
    if versionCount >= 30:
        versionCount = "30+"

    returnData = [
        team_name,
        project_data["name"],
        file_data["name"],
        file_data["key"],
        "https://www.figma.com/file/" + file_data["key"],
        file_data["relatedSlideDeck"],
        arrow.get(file_data["last_modified"]).date().isoformat(),
        lastUser,
        file_data["thumbnail_url"],
        versionCount,
        lastUserImg,
        label,
        description,
        ' '.join(tags)
    ]
    return returnData


@ app.route('/')
def main():
    global team_name
    team_name, project_list = getTeamAndProjects()
    projects_and_files = getProjectFiles(project_list)
    updateFilesWithDeeperData(projects_and_files)
    # saveLocalJSON(projects_and_files)  # for debugging help
    # projects_and_files = loadLocalJSON()
    updateGoogleSheet(projects_and_files)
    return make_response(jsonify(projects_and_files), 201)


def loadLocalJSON():
    with open('localJSON.json') as json_file:
        data = json.load(json_file, strict=False)
        return data


def saveLocalJSON(info):
    f = open("localJSON.json", "w+")
    f.write(json.dumps(info))
    f.close()


# Main body
if __name__ == "__main__":
    main()
    # app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
