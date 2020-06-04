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


# Env variables
spreadsheet_id = os.environ.get('spreadsheet_id')

# Global Vars

team_name = ""
headers = {
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Host': "api.figma.com",
    'accept-encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
}
service = build('sheets', 'v4')
plugin_id = '749778475482705952'

google_slide_deck_prefix = 'https://docs.google.com/presentation/d/'
buganizerPrefix = 'https://b.corp.google.com/issues/'
configRange = "config!B:C"


def getConfiguration():
    # Grab the set of configuration information from the spreadsheet
    request = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=configRange)
    response = request.execute()
    return response["values"][1:]


def getTeamAndProjects(team_id):
    url = "https://api.figma.com/v1/teams/" + team_id + "/projects"
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
        friendly_name = "Slide Deck"
        return createSheetsHyperlink(google_slide_deck_prefix + slideDeckID, friendly_name)
    except:
        return ""


def updateFilesWithDeeperData(projects_and_files):
    # for each file get the figamFileInfo
    for project in projects_and_files:
        for file in project["files"]:
            file["fileInfo"] = getFigmaFileInformation(file["key"])
            file["relatedSlideDeck"] = getFigmaFileSlideDeck(file["key"])


def updateGoogleSheet(projects_and_files, range_counter):
    for project in projects_and_files:
        for file_info in project["files"]:
            range_counter += 1
            range_name = 'raw_data!' + \
                str(range_counter) + ":" + str(range_counter)
            body = {
                'values': [figmaFileInfoToSheetStyle(file_info, project)]
            }
            result = service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption="USER_ENTERED", body=body).execute()
            print('{0} cells updated.'.format(result.get('updatedCells')))
    return range_counter


def getTags(description):
    # parse out all the #'s for tags and return them
    matches = []
    if description:
        regex = r"#\w+"
        matches = re.findall(regex, description, re.MULTILINE)
    return matches


def getRelatedBuganizerTicket(title):
    if title:
        regex = r"b/\d+"
        matches = re.findall(regex, title, re.MULTILINE)
        if matches:
            linkURL = buganizerPrefix + matches[0][2:]
            friendlyURL = "b/" + matches[0][2:]
            return createSheetsHyperlink(linkURL, friendlyURL)
    return ""


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
    # TODO How do we handle autosaves that lose the descriptions or tags??
    # Perhaps we create a plugin to manange this kind of data?
    figmaFileLink = createSheetsHyperlink(
        "https://www.figma.com/file/"+file_data["key"], "Figma File")

    versionCount = len(versions)

    returnData = [
        team_name,
        project_data["name"],
        file_data["name"],
        getRelatedBuganizerTicket(file_data["name"]),
        file_data["key"],
        figmaFileLink,
        file_data["relatedSlideDeck"],
        arrow.get(file_data["last_modified"]).date().isoformat(),
        createMomaPersonLink(lastUser),
        createSheetsImage(lastUserImg),
        createSheetsImage(file_data["thumbnail_url"]),
        versionCount,
        label,
        description,
        ' '.join(tags)
    ]
    return returnData


@ app.route('/')
def main():
    teamList = getConfiguration()
    range_counter = 1
    for team in teamList:  # Skip the header row
        global team_name, headers
        headers["X-FIGMA-TOKEN"] = team[0]
        team_id = team[1]
        team_name, project_list = getTeamAndProjects(team_id)
        print("Start: ", team_name + " []")
        projects_and_files = getProjectFiles(project_list)
        updateFilesWithDeeperData(projects_and_files)
        # saveLocalJSON(projects_and_files)  # for debuggingp
        # projects_and_files = loadLocalJSON() # for debugging
        range_counter = updateGoogleSheet(projects_and_files, range_counter)
        print("Complete: ", team_name + " [" + str(range_counter) + "]")
    return make_response("Thanks", 201)


#- Utilities -#

@app.template_filter()
def friendly_time(value):
    return arrow.get(value).humanize()


def createMomaPersonLink(name):
    momaSearchLink = "https://moma.corp.google.com/search/people?q=" + name
    return '=HYPERLINK("' + momaSearchLink + '", "' + name + '")'


def createSheetsHyperlink(url, friendly_name):
    return '=HYPERLINK("' + url + '", "' + friendly_name + '")'


def createSheetsImage(image_url):
    return '=IMAGE("' + image_url + '")'


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
    # main()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
