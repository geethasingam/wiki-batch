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
    pgTitle = i_row[4]
    pgDate = i_row[5]
    pgYear = pgDate[:4]
    pgMonth = pgDate[5:7]
    pgDay = pgDate[8:]
    pgLanguage = i_row[8]
    pgPeriodicity = i_row[9]
    pgPages = i_row[10]    
    pgCats = i_row[15]
    
    tamilMonths = {"01":"தை", "02":"மாசி", "03":"பங்குனி", "04":"சித்திரை", "05":"வைகாசி", "06":"ஆனி", "07":"ஆடி", "08":"ஆவணி", "09":"புரட்டாதி", "10":"ஐப்பசி", "11":"கார்த்திகை", "12":"மார்கழி"}

    pgMonth = translate(pgMonth, tamilMonths)

    pdfUrl = "http://noolaham.net" + pgFolderPath + "/" + pgNumber + ".pdf"
    pdfLink = "\n<!--pdf_link-->* [" + pdfUrl + " " + pgTitle + "] {{P}}<!--pdf_link-->\n"	

    pageParamsDict = {'title':pgTitle, 'number':pgNumber, 'date':pgDate, 'year':pgYear, 'pages':pgPages, 'langauge':pgLanguage, 'periodicity': pgPeriodicity, 'month':pgMonth, 'day':pgDay}

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
site = wiki.Wiki("https://yourwiki.org/api.php") 

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
        pgTitle = row[4]
        print pgTitle
        pageText = prepareWikiPage(row)
        updateWikiPage(site, api, token, pgTitle, pageText)	
		  		  
finally:
     batchfile.close()