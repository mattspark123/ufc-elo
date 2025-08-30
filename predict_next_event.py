from bs4 import BeautifulSoup
import pandas as pd
import requests
import sys
import elo_functions as elo
import os
import re

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
    }

    URL = 'https://en.wikipedia.org/wiki/List_of_UFC_events'
    
    page = requests.get(URL, headers = headers, timeout = 20)


    soup = BeautifulSoup(page.content,'html.parser')

    upcomingFightsTable = soup.find('table', id = 'Scheduled_events')
    upcomingFights = upcomingFightsTable.find_all('tr')
    event = upcomingFights[-1].find_all('td')
    eventLink = event[0].find('a').get('href')

    fightURL = 'https://en.wikipedia.org'+eventLink
    eventPage = requests.get(fightURL, headers = headers, timeout = 20)
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

    event = eventLink[6:] + '.txt'
    event = re.sub(r'[<>:"/\\|?*]', '', event)

    file_path = os.path.join('data','predictions',event)

    print(file_path)
    with open(file_path, 'w',encoding='utf-8') as f_out:
        for i, row in enumerate(fighterArray):
            f_out.write(f'Fight {i+1}\n')
            print(f'Fight {i+1}')

            fighter1_name = row[0].split('(')[0].strip().title()
            fighter2_name = row[1].split('(')[0].strip().title()

            if df.loc[df['Name'].str.title() == fighter1_name, 'Elo'].empty: 
                debut_msg1 = f'{fighter1_name} is making their debut in the UFC\n'
                print(debut_msg1.strip())
                f_out.write(debut_msg1)
                fighter1Elo = 1200
            else:
                fighter1Elo = df.loc[df['Name'].str.title() == fighter1_name, 'Elo'].iloc[0]

            if df.loc[df['Name'].str.title() == fighter2_name, 'Elo'].empty: 
                debut_msg2 = f'{fighter2_name} is making their debut in the UFC\n'
                print(debut_msg2.strip())
                f_out.write(debut_msg2)
                fighter2Elo = 1200
            else:
                fighter2Elo = df.loc[df['Name'].str.title() == fighter2_name, 'Elo'].iloc[0]

            probList = elo.eloProb(fighter1Elo, fighter2Elo)
            fighter1Odds = elo.calcOdds(probList[0])
            fighter2Odds = elo.calcOdds(probList[1])
            adjOdds = elo.adjustVig(fighter1Odds, fighter2Odds)

            result_text = (
                f'{row[0]} Wins: {probList[0]}% / {adjOdds[0]}\n'
                f'{row[1]} Wins: {probList[1]}% / {adjOdds[1]}\n\n'
            )
            print(result_text.strip())
            f_out.write(result_text)

main()
