from bs4 import BeautifulSoup
import pandas as pd
import requests
import sys
import elo_functions as elo

sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://en.wikipedia.org/wiki/List_of_UFC_events'
page = requests.get(URL)

soup = BeautifulSoup(page.content,'html.parser')

upcomingFightsTable = soup.find('table', id = 'Scheduled_events')
upcomingFights = upcomingFightsTable.find_all('tr')
event = upcomingFights[-1].find_all('td')
eventLink = event[0].find('a').get('href')

fightURL = 'https://en.wikipedia.org'+eventLink
eventPage = requests.get(fightURL)
eventPage.encoding = "utf-8"

eventSoup = BeautifulSoup(eventPage.content,'html.parser')

fightTable = eventSoup.find('h2',id = 'Fight_card').find_next('table',class_='toccolours')
fighterArray = []

for row in fightTable.find_all('tr')[2:]:
	if len(row) < 3: #skipping header rows
		continue
	nodeArray =[]
	nodeArray.append(row.find_all('td')[1].text.strip())
	nodeArray.append(row.find_all('td')[3].text.strip())
	fighterArray.append(nodeArray)
#print(fightTable.find_all('tr')[2])

df = pd.read_csv('data\\elo_list_output.csv')

for i,row in enumerate(fighterArray):
	print('Fight',i+1)
	if df.loc[df['Name'].str.title() == row[0].split('(')[0].strip().title(), 'Elo'].empty: 
		print(f'{row[0].split('(')[0].strip()} is making their debut in the UFC')
		fighter1Elo=1200
	else:
		fighter1Elo = df.loc[df['Name'].str.title() == row[0].split('(')[0].strip().title(), 'Elo'].iloc[0]

	if df.loc[df['Name'].str.title() == row[1].split('(')[0].strip().title(), 'Elo'].empty: 
		print(f'{row[1].split('(')[0].strip()} is making their debut in the UFC')
		fighter2Elo=1200
	else:
		fighter2Elo = df.loc[df['Name'].str.title() == row[1].split('(')[0].strip().title(), 'Elo'].iloc[0]

	probList = elo.eloProb(fighter1Elo,fighter2Elo)
	fighter1Odds = elo.calcOdds(probList[0])
	fighter2Odds = elo.calcOdds(probList[1])
	adjOdds = elo.adjustVig(fighter1Odds,fighter2Odds)

	print(f'{row[0]} Wins: {probList[0]}% / {adjOdds[0]}\n{row[1]} Wins: {probList[1]}%  / {adjOdds[1]}')
	print('\n')
