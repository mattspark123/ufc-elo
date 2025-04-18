import ufcelo_scraped as elo
import numpy as np
import pandas as pd
import csv
from rapidfuzz import fuzz, process

df = pd.read_csv('elo_list_output.csv')

entry1 = input('Enter first fighter\n')
entry2 = input('Enter second fighter\n')

# entry1 = 'Khabib'
# entry2 = 'Islam Machachev'

choices = df['Name'].tolist()
bestMatch = process.extractOne(entry1,choices)
bestMatch2 = process.extractOne(entry2,choices)

entry1=bestMatch[0]
entry2=bestMatch2[0]

fighter1 = df.loc[df['Name'] == entry1, 'Elo'].iloc[0]
fighter2 = df.loc[df['Name'] == entry2, 'Elo'].iloc[0]



probList = elo.eloProb(fighter1,fighter2)
fighter1Odds = elo.calcOdds(probList[0])
fighter2Odds = elo.calcOdds(probList[1])
adjOdds = elo.adjustVig(fighter1Odds,fighter2Odds)


print(f'{entry1} Wins: {probList[0]}% / {adjOdds[0]}\n{entry2} Wins: {probList[1]}%  / {adjOdds[1]}')