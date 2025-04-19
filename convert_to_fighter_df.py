import numpy as np
import pandas as pd


df = pd.read_csv('data\\processed_wikipedia_df.csv')
df = df.drop(df.columns[:2], axis =1)



df_w = df.copy()
df_l = df.copy()

df_w=df_w.rename(columns={'Winner' : 'Fighter', 'Loser':'Opponent', 'Winner_Pre_Elo':'Pre_Elo' , 'Winner_Post_Elo':'Post_Elo', 'WinStreak':'Streak','winnerFightCount' : 'FightCount'})
df_l=df_l.rename(columns={'Loser' : 'Fighter', 'Winner':'Opponent', 'Loser_Pre_Elo':'Pre_Elo' , 'Loser_Post_Elo':'Post_Elo', 'Loser_brokenStreak':'Streak','loserFightCount' : 'FightCount'})


df_w.drop(columns=['Loser_Pre_Elo',  'Loser_Post_Elo','Loser_brokenStreak'], inplace=True)
df_l.drop(columns=['Winner_Pre_Elo', 'Winner_Post_Elo','WinStreak'], inplace=True)

df_w['Result'] = 'W'
df_l['Result'] = 'L'
df_combined = pd.concat([df_l,df_w])

df_combined=df_combined.sort_values(by = 'Date')
df_combined.reset_index(inplace = True)

column_order=['Date', 'Event', 'Fighter', 'Opponent', 'Streak', 'Pre_Elo', 'Post_Elo', 'WeightClass', 'Result', 'Method', 'Method_Notes', 'Round', 'Time', 'ConvertedTime', 'isTitleBout', 'K_Value','FightCount']
df_combined=df_combined[column_order]
df_combined.to_csv('data\\fighter_df.csv', index=True)




