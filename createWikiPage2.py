# -*- coding: utf-8 -*-
import urllib
import ftplib
import os
import csv
import sys
from string import Template
from wikitools import wiki
from wikitools import api

def getNoolahamToken(i_site, i_api):
     params = {'action':'query', 'prop':'info','intoken':'edit','titles':'1'}
     req = i_api.APIRequest(i_site, params)
     response = req.query(False)
     token = response['query']['pages']['-1']['edittoken']
     return token

def updateWikiPage(i_site, i_api, i_token, i_titlePage, i_updateText):
     params = {'action':'edit', 'title':i_titlePage, 'token':i_token,  'text': i_updateText}
     request = i_api.APIRequest(i_site, params)
     result = request.query()
     print result
     return

def getCatsText(i_catsStr):
    catsList = i_catsStr.split(";")
    catText = "\n"
    for cat in catsList:
        catText = catText = "[[பகுப்பு:" + cat + "]]\n"
    return catText

def prepareWikiPage(i_row):
    pgNumber = i_row[0]
    pgFolderPath = i_row[1]
    pgTitle = i_row[2]
    pgDate = i_row[3].strip()
    pgYear = pgDate[:4]
    pgMonth = pgDate[5:7]
    pgDay = pgDate[8:]
    pgContentType = i_row[4].strip()
    pgLanguage = i_row[6]
    pgPeriodicity = i_row[7].strip()
    pgPages = i_row[13]
    pgAuthor = i_row[8]
    pgPublisher = i_row[9]
    pgCats = i_row[16]

    pdfUrl = "http://noolaham.net" + pgFolderPath + "/" + pgNumber + ".pdf"
    pdfLink = "\n<!--pdf_link-->* [" + pdfUrl + " " + pgTitle + "] {{P}}<!--pdf_link-->\n"

    pageParamsDict = {'contentType':pgContentType, 'title':pgTitle, 'number':pgNumber, 'date':pgDate, 'year':pgYear, 'pages':pgPages, 'langauge':pgLanguage, 'periodicity': pgPeriodicity, 'month':pgMonth, 'day':pgDay, 'author':pgAuthor, 'publisher':pgPublisher, 'category':pgCats}

    pageText = ""
    if pgContentType == "இதழ்":
        pageText = """{{$contentType|
    நூலக எண் = $number |
    வெளியீடு = [[:பகுப்பு:$year|$year]].$month.$day  |
    சுழற்சி = $periodicity |
    இதழாசிரியர் = $author |
    மொழி = $langauge |
    பதிப்பகம் = $publisher |
    பக்கங்கள் = $pages |
    }}

=={{Multi|வாசிக்க|To Read}}==
"""

    if pgContentType == "நூல்" or pgContentType == "பிரசுரம்":

        pageText = """{{$contentType|
    நூலக எண் = $number |
    வெளியீடு = [[:பகுப்பு:$year|$year]].$month.$day  |
    ஆசிரியர் = $author |
    வகை=$category|
    மொழி = $langauge |
    பதிப்பகம் = $publisher |
    பதிப்பு = [[:பகுப்பு:$year|$year]] |
    பக்கங்கள் = $pages |
    }}

=={{Multi|வாசிக்க|To Read}}==
"""


    if pgContentType == "பத்திரிகை":

        tamilMonths = {"01":"தை", "02":"மாசி", "03":"பங்குனி", "04":"சித்திரை", "05":"வைகாசி", "06":"ஆனி", "07":"ஆடி", "08":"ஆவணி", "09":"புரட்டாதி", "10":"ஐப்பசி", "11":"கார்த்திகை", "12":"மார்கழி"}
        pgMonth = translate(pgMonth, tamilMonths)
        pageParamsDict["month"] = pgMonth

        pageText = """{{பத்திரிகை|
நூலக எண் = $number |
வெளியீடு = $month $day, [[:பகுப்பு:$year|$year]]  |
சுழற்சி = $periodicity |
மொழி = $langauge |
பக்கங்கள் = $pages |
}}

=={{Multi|வாசிக்க|To Read}}==
"""

    paramReplace = Template(pageText)
    pageText = paramReplace.substitute(pageParamsDict)

    #Add pdf link
    pageText = pageText +  pdfLink;

    #Add year category
    pageText = pageText + "\n\n" + "[[பகுப்பு:" + pgYear + "]]";

    #Add other categories
    catsStr = getCatsText(pgCats)
    pageText = pageText + catsStr

    return pageText


def translate(string, wdict):
    for key in wdict:
        string = string.replace(key, wdict[key].lower())
    return string.upper()

# create a Wiki object
site = wiki.Wiki("http://yourwiki.org/api.php")

# login - required for read-restricted wikis
if not site.login("Username ", "Password", verify=True):
    print("Login failed")

#Get Token (needed to edit wiki)
token = getNoolahamToken(site, api)

#Read through each entry and update wiki
batchfile = open('createdata.csv', 'rt')
try:
     reader = csv.reader(batchfile)
     for row in reader:
        pgTitle = row[2]
        pageText = prepareWikiPage(row)
        print(pageText)
        updateWikiPage(site, api, token, pgTitle, pageText)

finally:
     batchfile.close()
