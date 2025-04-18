from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv
import time
import random
import os
from datetime import datetime
import find_files as ff

#pd.set_option('display.max_columns', None)

URL = 'https://en.wikipedia.org/wiki/List_of_UFC_events'
page = requests.get(URL)

#print(page.text)

soup = BeautifulSoup(page.content,'html.parser')

#Find table for all events on UFC Events page
fightTable = soup.find('table', id="Past_events" )
fights = fightTable.find_all('tr')

#Get hrefs from the table, and write to list
links = []
eventDates = []
for row in fights[1:]: #1: to skip headers
	cells = row.find_all('td')
	#print(cells[0].text,'\n')
	if len(cells[0].text.strip())==3: #events that were cancelled don't have a number, cells[0] holds the index in the wiki table
		link=cells[1].find('a')
		links.append(link.get('href'))
		eventDates.append(datetime.strptime(cells[2].text.strip(),'%b %d, %Y').date())
			
#Reverse so that data is written chronologically, initialize list to write to df later
links.reverse()
eventDates.reverse()
allFights = []

#Open the file, read last line to see where we left off
last_line = ff.findLastLine('raw_wikipedia_parsed_df.csv')

#Set point to continue, or from beginning if it file doesn't exist or something
if last_line in links and last_line != links[-1]:
	last_event_index = links.index(last_line)
	last_event_index+=1
	print('Updates found:')
elif last_line == links[-1]:
	print('No updates to make. Quitting...')
	quit()
else:
	last_event_index = 0
	print('File not found. Rescraping...')

#Iterating through all events' wiki pages, parsing
for eventLink,eventDate in zip(links[last_event_index:],eventDates[last_event_index:]):
	eventURL = 'https://en.wikipedia.org' + eventLink
	eventPage = requests.get(eventURL)
	eventSoup = BeautifulSoup(eventPage.content,'html.parser')
	print('Scraping ' + eventURL)
	#for each page, find the table with fights
	eventFightTable = eventSoup.find_all("table", class_= 'toccolours')
	#once table found, break it down by row
	eventFightList = eventFightTable[-1].find_all('tr')
	time.sleep(random.uniform(1, 2)) #so I don't get IP banned from wikipedia

	for row in eventFightList:
		cells = row.find_all(['td','th'])
		if len(cells) < 2: #skipping header rows
			continue
		if cells[0].text.strip().lower() in ('weight', 'weight class') : #skip column name rows
			continue
		if len(cells) >=6:
			event = eventLink #to be used as key for date later
			weight_class = cells[0].text.strip()
			winner = cells[1].text.split('(')[0].strip()
			result = cells[2].text.split('.')[0].strip()
			loser = cells[3].text.split('(')[0].strip()
			method = cells[4].text.upper().strip()
			method_notes = cells[4].text.strip()
			round_ = cells[5].text.strip() if cells[5].text.strip() else 'N/A' #there used to be no rounds so we need to handle this case
			time_ = cells[6].text.strip() if cells[6].text.strip() else 'N/A'
			isTitle = True if cells[1].text.strip().endswith('(c)') else False
			time_conv = 'N/A'

			if 'NO CONTEST' in method:
				method = 'NC'
			elif 'DRAW' in method:
				method = 'DRAW'
			elif 'DISQUALIFICATION' in method:
				method = 'DQ'
			elif 'SUBMISSION' in method:
				method = 'SUB'
			elif 'UNANIMOUS' in method:
				method = 'UD'
			elif 'MAJORITY' in method:
				method = 'MD'
			elif 'SPLIT DECISION' in method:
				method = 'SD'
			elif 'INJURY' in method:
				method = 'INJURY'

			if time_ != 'N/A':
				minutes, seconds = map(int, time_.split(':'))
				time_conv = minutes * 60 + seconds


			#print('Writing ',winner,' ', result,' ',loser)
			allFights.append({
	    		"Event": event
	    		,"Date": eventDate
	    		,"WeightClass" : weight_class
	    		,"Winner" : winner
				,"Result" : result
				,"Loser" : loser
				,"Method" : method.split('(')[0].strip()
				,"Method_Notes" : method_notes
				,"Round" : round_
				,"Time" : time_
				,"ConvertedTime" : time_conv
				,"isTitleBout" : isTitle
				,"WinStreak" : 0
	    		})

#pprint.pprint(allFights)
df = pd.DataFrame(allFights)

#check to see whether to overwrite entirely, or to append new info
if last_event_index == 0:
	df.to_csv('raw_wikipedia_parsed_df.csv')
else:
	ff.deleteLastLine('raw_wikipedia_parsed_df.csv')
	df.to_csv('raw_wikipedia_parsed_df.csv',mode='a',header = False)

with open('raw_wikipedia_parsed_df.csv', 'a') as file:
    file.write(links[-1]) 


