# UFC Web Scraper / Elo Calculator

I applied the Chess Elo formula to all UFC fights to find out who the best actually is! FYI it's currently **Islam Makhachev**, but of course this is subject to change.

I wasn't able to find good, all-encompassing datasets on Kaggle so I built my own webscraper to iteratively parse Wikipedia's UFC events pages to build a fresh historical fight record.

Then, I use 'pandas' to iterate through this parsed data and construct a dataframe, from which I am able to apply the formula, on top of other metrics I'm tracking.

The goal here wasn't to make a super-accurate betting assistant, it was more of an exercise in building an ETL Pipeline and then working with the data afterwards for fun.

## data_parser.py
Written with `Beautiful Soup 4`, accesses current file to see where results last left off, and then parses events that happened since the last run. Stores a bunch of column information (like using the event link as a batch identifier, previous and new elos, method of victory, etc) and writes to a csv for processing. Also performs a lot of cleaning and sorting of data scraped, for example it tries to standardize names by using various string manipulations.

## find_files.py
Quick functions just to help the data parser know where it left off.

## elo_functions.py
Houses all the probability/Elo functions I use in my calculations. This is probably the most fiddly bit-- I try to weight various methods/times/circumstances of victory differently

## calculate_elos.py
Actually performs the Elo calculations using the output from data_parser.py. Tracks same info as the raw csv but calculates other metrics using a combination of vectorized/unvectorized functions, e.g. Win streak, total fight count, last fight, previous and new Elo rating, etc.

## head2head.py
Uses a fuzzy match via `rapidfuzz` to allow two fighters to be inputted by user, and then compares elos to generate win probability and bettings odds (adjusted for vig) for each.

## predict_next_event.py
Uses similar logic to `head2head.py` but looks for the next event and calculates for all fighters on that card.

## convert_to_fighter_df.py
Converts the processed df from 'calculate_elos.py', and then doubles up results so that every fighter has a row represented, per fight. This makes it much easier to track fighter statistics across time when I load into PowerBI or other BI/Vis tools. 
