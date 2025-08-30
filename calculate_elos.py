import elo_functions as elo_f
import numpy as np
import pandas as pd
import csv
import sys
from datetime import datetime,date

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    df = pd.read_csv("data\\raw_wikipedia_parsed_df.csv",skipfooter=1, engine='python')
    df['Winner'] = df['Winner'].str.strip().str.lower().str.title() #clean minor name variations/typos
    df['Loser'] = df['Loser'].str.strip().str.lower().str.title()
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    df = df.drop_duplicates(subset = ['Event','Winner'],keep='first').reset_index(drop=True) #basically if the subset values match, two rows are considered dupes
    df=df.sort_values(by = 'Date')
    elo_dict= {}

    for index,row in df.iterrows():
        #for both red and blue, if they exist, access value
        #if they don't, add them to the dictionary with 1200 elo rating
        if row['Winner'] not in elo_dict:
            elo_dict[row['Winner']] = {'elo': 1200, 'winStreak' : 0, 'last_fight' : 0, 'total_fights' : 0}
            
        if row['Loser'] not in elo_dict:
            elo_dict[row['Loser']] = {'elo': 1200, 'winStreak': 0, 'last_fight' : 0, 'total_fights' : 0}
        
        #directly writing to dataframe so we have historical elo data
        df.at[index,'Winner_Pre_Elo'] = elo_dict[row['Winner']]['elo']
        df.at[index,'Loser_Pre_Elo'] = elo_dict[row['Loser']]['elo']
        df.at[index,'Loser_brokenStreak'] = elo_dict[row['Loser']]['winStreak']

        elos_updates = elo_f.calc_elo(elo_dict[row['Winner']]['elo']
            ,elo_dict[row['Loser']]['elo']
            ,row['Method']
            ,row['Round']
            ,row['ConvertedTime']
            ,row['isTitleBout']
            ,elo_dict[row['Winner']]['winStreak']
            ,row['Date'])

        #update all values in dictionary
        elo_dict[row['Winner']]['elo'] = elos_updates[0]
        elo_dict[row['Loser']]['elo'] = elos_updates[1]

        elo_dict[row['Winner']]['total_fights'] += 1
        elo_dict[row['Loser']]['total_fights'] += 1

        if row['Method'] in ('DRAW', 'NC'):
            elo_dict[row['Winner']]['winStreak'] = 0
            elo_dict[row['Loser']]['winStreak'] = 0
        else:
            elo_dict[row['Winner']]['winStreak'] += 1
            elo_dict[row['Loser']]['winStreak'] = 0

        elo_dict[row['Winner']]['last_fight'] = row['Date']
        elo_dict[row['Loser']]['last_fight'] = row['Date']
        
        #more df data
        df.at[index,'Winner_Post_Elo'] = elos_updates[0]
        df.at[index,'Loser_Post_Elo'] = elos_updates[1]
        df.at[index, 'K_Value'] = elos_updates[2]
        #df.at[index,'Winner_winStreak'] = elo_dict[row['Winner']]['winStreak']
        df.at[index,'WinStreak'] = elo_dict[row['Winner']]['winStreak']
        df.at[index,'winnerFightCount'] = elo_dict[row['Winner']]['total_fights']
        df.at[index,'loserFightCount'] = elo_dict[row['Loser']]['total_fights']

    #export DF to csv
    df.to_csv('data\\processed_wikipedia_df.csv') 


    # Apply Elo Decay Before Sorting
    adjusted_elo_dict = {}

    for key, value in elo_dict.items():
        elo = value.get('elo', 1200)  # Default to 1200 if missing
        win_streak = value.get('winStreak', 0)
        last_fight = value.get('last_fight', date.today())  # Default to today if missing

        # Ensure last_fight is a valid date
        if isinstance(last_fight, int):  
            continue  # Skip invalid dates

        # Apply Elo Decay if Less Than 3 Years (1095 Days)
        days_since = (date.today() - last_fight).days
        if days_since < 1095:
            elo = elo * (0.99995 ** days_since)

        # Store Adjusted Values in New Dictionary
        adjusted_elo_dict[key] = {'elo': elo, 'winStreak': win_streak, 'last_fight': last_fight}

    # Sort Fighters by Adjusted Elo
    sorted_dict = dict(sorted(adjusted_elo_dict.items(), key=lambda item: item[1]['elo'], reverse=True))

    # Print Top 50 Fighters
    i = 1
    for fighter, data in sorted_dict.items():
        print(f"{i}: {fighter}: {data['elo']:.2f}, Last Fight: {data['last_fight']}".encode('utf-8', 'replace').decode('utf-8'))
        i += 1
        if i == 51:
            break

    # Write Sorted Elo Data to CSV
    with open('data\\elo_list_output.csv', 'w', encoding='utf-8') as csvfile:
        csvfile.write("Name,Elo,WinStreak,LastFight\n")
        
        for key, value in sorted_dict.items():
            elo = value['elo']
            win_streak = value['winStreak']
            last_fight = value['last_fight']
            
            csvfile.write(f'{key},{elo},{win_streak},{last_fight}\n')

main()
