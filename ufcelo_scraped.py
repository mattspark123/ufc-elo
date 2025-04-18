import numpy as np
import pandas as pd
from datetime import datetime,date

#Defining functions to calculate probability

def underdogProb(odds):
    return (abs(odds) / (abs(odds) + 100))


def favoriteProb(odds):
    return (100 / (odds + 100))

def calcOdds(prob):
    prob = prob / 100  # Convert percentage to decimal
    if prob > 0.5:  # Favorite
        odds = round(-(prob / (1 - prob)) * 100, 2)
    else:  # Underdog
        odds = round(100 / prob, 2)
    return odds

def adjustVig(prob1,prob2):
    vigList = []
    vigList.append(round(100*prob1/(prob1+prob2),-1))
    vigList.append(round(100*prob2/(prob1+prob2),-1))
    return vigList

#Calculate probability based on American odds. Adjusts for vig and returns a list, in same order provided
def probability(red_odds,blue_odds):
    if red_odds > 0 and blue_odds < 0:
        red_prob=favorite(red_odds)
        blue_prob=underdog(blue_odds)

    elif red_odds < 0 and blue_odds > 0:
        blue_prob=favorite(blue_odds)
        red_prob=underdog(red_odds)

    #in the case of even odds, assume both are underdogs
    else:
        red_prob=underdog(red_odds)
        blue_prob=underdog(blue_odds)

    #adjust for vig, write results to list
    vig_red = red_prob/(red_prob+blue_prob)
    vig_blue = blue_prob/(red_prob+blue_prob)
    adjusted_probs=[vig_red,vig_blue]

    return adjusted_probs

# Given winner and loser elo/context of bout, calculates new elos and returns them in list, along with final k value
def calc_elo(winner_elo,loser_elo,method,round_,time_conv,isTitle,winStreak,fightDate):
    k=75 # adjust value to change how volatile results are
    
    if (round_ == 1) and (time_conv<=300):
        k *= 1.3 - (0.3 * (time_conv / 300))

    if isTitle:
        k=k*1.1
    
    if method == 'KO':
        k = k * 1.08
    elif method in{'TKO','SUB'}:
        k = k * 1.04
    elif (method == 'INJURY') and (round_<3):
        k = 75

    #k=k*(.99995**(date.today()-datetime.strptime(fightDate, "%Y-%m-%d").date()).days)
    k=k*(.99995**(date.today()-fightDate).days)

    #reminder -- expected scores add up to 1
    expected_score_w = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    expected_score_l = 1 - expected_score_w

    # try:
    #     winStreak = int(winStreak)
    # except (ValueError, TypeError):
    #     winStreak = 0

    if method in ('DRAW', 'NC', 'DQ'): #draws
        new_winner_elo = winner_elo + k * (.5-expected_score_w)
        new_loser_elo = loser_elo + k * (.5-expected_score_l)
    
    elif winStreak > 0:
        new_winner_elo = winner_elo + (k * min(1.015**winStreak,1.3)) * (1 - expected_score_w)
        new_loser_elo = loser_elo + k * (0-expected_score_l)

    else:
        new_winner_elo = winner_elo + k * (1-expected_score_w)
        new_loser_elo = loser_elo + k * (0-expected_score_l)

    calculated_elo = [new_winner_elo,new_loser_elo,k]
    
    return calculated_elo



def eloProb (elo1,elo2):
    expectedScore1 = 1 / (1 + 10 ** ((elo2 - elo1) / 400))
    expectedScore2 = 1 - expectedScore1

    expectedScores=[float(round(100*expectedScore1,3)),float(round(100*expectedScore2,3))]
    return expectedScores

#print(eloProb(1946.7091043667008,1695.2411349565764))
