# figma-project-file-sync-to-drive
Utility to get a listing of Team Projects and Files and write them to a shared doc.

## Notes
Can we add tagging somehow to allow for easier searching?
	e.g. filtering, master/detail views, triggers
Who last updated the file? Or owner info?
Move this into G Sheets for the sorting/filtering etc.
Related Slide deck link
Should we back it with a real data store and then use sheets/data dashboard to slice/dice.
	Which would work best? firebase, firestore, datastore, sql? other?

How can we track what's approved? in production etc? 
Tagging by frame names? File Names, Dedicated pages?
Can we mark status and trigger with cloud functions, notifications when "review needed"


## Updates
Should sort by last updated.

## Why?
Birds eye view of team work
Good for onboarding.

## Spreadsheet
https://docs.google.com/spreadsheets/d/1m4T72la8TcogXLECMGspXJkeWfPv0YxJ9-eJlGagLjs/edit#gid=0


## Plugins
https://www.figma.com/community/plugin/749778475482705952/Sync-to-Slides

https://www.figma.com/file/RwLRoiiage5tSarrPayful/Apps-on-CR-Conceptspo


https://docs.google.com/presentation/d/1Tf6F-BzISslLBAWYnkB0LY52yaNtzTH4xvAqa4qk0XQ

https://docs.google.com/presentation/d/1Tf6F-BzISslLBAWYnkB0LY52yaNtzTH4xvAqa4qk0XQ/edit#slide=id._76:1_950809884


Links are getting stripped at :'s 
Fixed that. 
Need to look in the styleOverrideTable to and the ones that are 'hyperlink' and get the url 

respJson["nodes"][metadata_node_id]["document"]["children"][0]['children'][4]
    ['styleOverrideTable']['4']['hyperlink']['url']
'https://docs.google.com/presentation/d/1eyhLnHO8fZFC1gYYtYFG30bkxt3rFPmoXXb7oCWJ3qc/edit#slide=id.p'

