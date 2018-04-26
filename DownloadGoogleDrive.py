from __future__ import print_function
import httplib2
import os
import io
import shutil
import random
import sys
import time
import re

from apiclient.discovery import build as discovery_build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from json import dumps as json_dumps
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage as CredentialStorage
from oauth2client.tools import run_flow as run_oauth2
from urllib2 import urlopen

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from datetime import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Sync Google Drive Files'

def get_credentials():

    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sync-drive-files.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def from_File(query):
	data=[]
	file=open("config.txt","r")
	data=file.readlines()
	file.close()
	data2 = map(lambda each:each.splitlines(),data)
	
	if (query=='Sync'):
		return re.sub(r'.*=', '', data2[0][0])
	elif  (query=='folderId'):
		return re.sub(r'.*=', '', data2[1][0])
	elif  (query=='output'):
		return re.sub(r'.*=', '', data2[2][0])
	else:
		return ''
	return ''
	
def google_doc(fileType):
	google_document="application/vnd.google-apps.document"
	google_spreadsheet="application/vnd.google-apps.spreadsheet"
	google_map="application/vnd.google-apps.map"
	google_form="application/vnd.google-apps.form"
	google_folder="application/vnd.google-apps.folder"
	google_file="application/vnd.google-apps.file"
	google_drawing="application/vnd.google-apps.drawing"
	google_presentation="application/vnd.google-apps.presentation"
	
	if fileType == google_document:
		return True
	if fileType == google_spreadsheet:
		return True
	if fileType == google_form:
		return True
	if fileType == google_folder:
		return True
	if fileType == google_file:
		return True
	if fileType == google_drawing:
		return True
	if fileType == google_presentation:
		return True		
	else :
		return False

def add_Folder(folderName):
	data=[]
	fileName="config.txt"
	file=open(fileName,"r")
	data=file.readlines()
	file.close()
	file=open(fileName,"w+")
	data[2] = data[2]+"/"+folderName
	file.writelines(data)
	file.close()
	return True

def remove_Folder(folderName):
	data=[]
	fileName="config.txt"
	file=open(fileName,"r")
	data=file.readlines()
	file.close()
	file=open(fileName,"w+")
	data[2] = data[2]+"/"+folderName
	data[2]=data[2][:data[2].find("/"+folderName)]
	file.writelines(data)
	file.close()
	return True			
		
def write_Sync_Time():
	data=[]
	fileName="config.txt"
	file=open(fileName,"r")
	data=file.readlines()
	file.close()
	file=open(fileName,"w+")
	newTime = urlopen('http://just-the-time.appspot.com/')
	time_str = newTime.read().strip()
	time_str = time_str.replace(" ", "T")
	data[0] = "Sync="+time_str+"\n"
	file.writelines(data)
	file.close()
	return time_str	

def read_File(query):
	data=[]
	file=open("config.txt","r")
	data=file.readlines()
	file.close()
	data2 = map(lambda each:each.splitlines(),data)
	
	if (query=='Sync'):
		return re.sub(r'.*=', '', data2[0][0])
	elif  (query=='FolderId'):
		return re.sub(r'.*=', '', data2[1][0])
	elif  (query=='output'):
		return re.sub(r'.*=', '', data2[2][0])
	else:
		return ''
	return ''
	
def check_Directory(directory_Name):
	if not os.path.exists(directory_Name):
		os.makedirs(directory_Name)
	return
	
	
def get_file(fileID,name,service):
	file=name
	directory="./"+from_File('output')+"/"
	check_Directory(directory)
	destiny= directory+file
	fh = io.FileIO(file, 'wb')
	q = service.files().get_media(fileId=fileID)
	downloader = MediaIoBaseDownload(fh, q)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
	fh.close()
	shutil.move(file,destiny)
	return 
	
def export_file(fileID,name,service):
	file=name
	directory="./"+from_File('output')+"/"
	check_Directory(directory)
	destiny= directory+file+".pdf"
	fh = io.FileIO(file, 'wb')
	q = service.files().export_media(fileId=fileID,mimeType='application/pdf')
	downloader = MediaIoBaseDownload(fh, q)
	done = False
	while done is False:
		status, done = downloader.next_chunk()
	fh.close()
	shutil.move(file,destiny)
	return 	
	
def query_filter(folder):
	not_Trashed =' and trashed != True'
	modified_Time = ''
	sync_Time= from_File('Sync')
	if(sync_Time>''):
		modified_Time=" and modifiedTime > '"+sync_Time+"'"
	return folder+not_Trashed+modified_Time

def getService():
	credentials = get_credentials()
	http = credentials.authorize(httplib2.Http())
	return discovery.build('drive', 'v3', http=http)
	
def fileList(folder):

	service = getService()
	result = service.files().list(fields="files(id,name,mimeType,modifiedTime)",
        q=query_filter(folder), includeTeamDriveItems='True',supportsTeamDrives='True').execute()
	items = result.get('files', [])
	return result

def downloadFiles(results):
	
	service = getService()
	items = results.get('files', [])
	if not items:
		print('No new files found.')
	else:
		print('Downloading:')
		for item in items:
			print('{0}'.format(item['name']))
			if not google_doc(item['mimeType']):
				get_file(item['id'],item['name'],service)
			elif(item['mimeType']=='application/vnd.google-apps.folder'):
				folderitem=1;
				add_Folder(item['name'])
				folder = "'"+item['id']+"'"+" in parents"
				downloadFiles(fileList(folder))
				remove_Folder(item['name'])
			else:
				export_file(item['id'],item['name'],service)
	return 
	
def main():

	folder = "'"+from_File('folderId')+"'"+" in parents"
	downloadFiles(fileList(folder))
	write_Sync_Time()
	print('Done')	
if __name__ == '__main__':
    main()
