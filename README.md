# Figma Projects & Files Listing

## What is it

Utility to get a listing of Teams Projects and Files and write them into a shared Google Spreadsheet

## Why does this exist

1. Birds eye view of multiple teams work
1. Great for onboarding and understanding what's being worked on
1. Helps make work shareable across teams and orgs 


### Bugs to fix

1. Counter of items created is incorrect (and the range counter passed around is odd)

### Bugs fixed

    Links are getting stripped at :'s 
    Parse through styleOverrideTable to find urls that are type 'hyperlink' 
    Need to add write empty values into all of the Metadata fields in case the ordering changes (so we're not left with unrelated metadata in the spreadsheet attached to incorrect figma files)


### Updates Needed

1. More documentation of functions so it's easier to remember what I was thinking when I wrote things.
1. Create a branded resource site to promote and share
1. Get certified for G open source sharing

---

#### GCP Related things (not relevant to external users)

## The spreadsheet for GCP

[Figments Spreadsheet](https://docs.google.com/spreadsheets/d/1m4T72la8TcogXLECMGspXJkeWfPv0YxJ9-eJlGagLjs/edit#gid=0)

## Figma Plugins  

[Sync to Slides](https://www.figma.com/community/plugin/749778475482705952/Sync-to-Slides)

The application looks for this plugin and pulls the related Google Slides deck from it.
