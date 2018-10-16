# -*- coding: utf-8 -*-
import ftplib
import os
import csv
import sys
import time

# Uploads the html file to the noolaham.net server
def uploadToServer(i_session, i_ftppath, i_htmldir, i_htmlfile):
     print "Uploading file: " + i_htmlfile
     i_ftppath = i_ftppath.replace("/project", "")
     i_session.cwd(i_ftppath)
     os.chdir(i_htmldir)
     file = open(i_htmlfile,'rb')                  		# file to send
     i_session.storbinary('STOR ' + i_htmlfile, file)     	# send the file
     file.close()                                    	# close file and FTP
     return 
     
def downloadFile(i_fileURL):
    command = "wget " + i_fileURL + " -P data"
    print "download: " + command
    os.system(command)    
                                
def createCoverImage(i_fileName):
    command = "java -jar LinkTester.jar ccp " + i_fileName
    os.system(command)
    
session = ftplib.FTP('sever','username','p.w')
tooldir = r"/var/www/html"
datadir = os.path.join(tooldir, "data")

#Read through each entry and update wiki
batchfile = open('createdata.csv', 'rt')
try:
     reader = csv.reader(batchfile)
     for row in reader:        
        os.chdir(tooldir)
        pgNoolahamNum = row[0]
        pgFolderPath = row[1]
        pgURL = "http://noolaham.net" + pgFolderPath + "/" + pgNoolahamNum + ".pdf"
        print "processing " + pgURL
        downloadFile(pgURL)  
        createCoverImage("data/" + pgNoolahamNum + ".pdf")
        uploadToServer(session, pgFolderPath, datadir, pgNoolahamNum + ".JPG")
  
finally:
     batchfile.close()
     

session.quit()
