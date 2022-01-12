from nsetools import Nse
from nsepython import *
import pandas as pd
import numpy as np
import praw
import requests
import json

nse = Nse()
# Making Losers DataFrame
losers = nse.get_top_losers()
loser_columns = ["Losers", "Change"]
loser_df = pd.DataFrame(columns = loser_columns)
for stock in losers:
    loser_df = loser_df.append(
        pd.Series(
            [
                stock['symbol'],
                str(stock['netPrice'])+"%"
            ], index = loser_columns
        ), ignore_index = True
    )
loser_df.index = np.arange(1, len(loser_df)+1)

# Making Losers DataFrame
gainers = nse.get_top_gainers()
gainer_columns = ["Gainers", "Change"]
gainer_df = pd.DataFrame(columns = gainer_columns)
for stock in gainers:
    gainer_df = gainer_df.append(
        pd.Series(
            [
                stock['symbol'],
                str(stock['netPrice'])+"%"
            ], index = gainer_columns
        ), ignore_index = True
    )
gainer_df.index = np.arange(1, len(gainer_df)+1)

# Getting Indices Data
indices = nse_index()
sectoral_columns = ["Index", "Change"]
sectors_list = ["NIFTY 50", "NIFTY AUTO", "NIFTY BANK", "NIFTY CONSUMER DURABLES", "NIFTY FIN SERVICE", "NIFTY FMCG", "NIFTY HEALTHCARE INDEX", "NIFTY IT", "NIFTY MEDIA", "NIFTY METAL", "NIFTY OIL & GAS", "NIFTY PHARMA", "NIFTY PVT BANK", "NIFTY PSU BANK", "NIFTY REALTY"]

# Making Sectoral DataFrame
sectoral_df = pd.DataFrame(columns = sectoral_columns)
for index, row in indices.iterrows():
    if row['indexName'] in sectors_list:
        sectoral_df = sectoral_df.append(
            pd.Series(
                [
                    row['indexName'],
                    str(row['percChange'])+"%"
                ], index = sectoral_columns
            ), ignore_index = True
        )
sectoral_df.index = np.arange(1, len(sectoral_df)+1)

# Making fiidii DataFrame
fiidii_columns = ['Category', 'Date', 'Buy', 'Sell', 'Net']
fiidii_df = pd.DataFrame(columns = fiidii_columns)
for index, row in nse_fiidii().iterrows():
    fiidii_df = fiidii_df.append(
        pd.Series(
            [
                row['category'][:-2],
                row['date'],
                row['buyValue'],
                row['sellValue'],
                row['netValue']
            ], index = fiidii_columns    
        ), ignore_index = True
    )
fiidii_df.index = np.arange(1, len(fiidii_df)+1)

# Getting Options Data
options = option_chain('NIFTY')
atm = options['records']['underlyingValue']
atm = 50*round(atm/50)
exp = '27-Jan-2022'
sliced_data = options['records']['data'][120:700]

# Put Options OI Data
option_columns = ['Strike Price', 'Open Interest']
pe_df = pd.DataFrame(columns = option_columns)
for strike in range(atm - 250, atm + 251, 50):
    for info in sliced_data:
        if(('PE' in info.keys()) and (info['strikePrice'] == strike) and (info['expiryDate'] == exp)):
            oi = info['PE']['openInterest']
            pe_df = pe_df.append(
                pd.Series(
                    [
                        info['strikePrice'],
                        oi
                    ], index = option_columns
                ), ignore_index = True
            )
pe_df.index = np.arange(1, len(pe_df)+1)

# Call Options OI Data
ce_df = pd.DataFrame(columns = option_columns)
for strike in range(atm - 250, atm + 251, 50):
    for info in sliced_data:
        if(('CE' in info.keys()) and (info['strikePrice'] == strike) and (info['expiryDate'] == exp)):
            oi = info['PE']['openInterest']
            ce_df = ce_df.append(
                pd.Series(
                    [
                        info['strikePrice'],
                        oi
                    ], index = option_columns
                ), ignore_index = True
            )
ce_df.index = np.arange(1, len(ce_df)+1)

#Creating Caption for Reddit Post
nsecaption = "Gainers/Losers:- \n\n"
nsecaption += gainer_df.to_string(col_space=20, justify='center', index = False) + "\n\n"
nsecaption += loser_df.to_string(col_space=20, justify='center', index = False) + "\n\n"

nsecaption += "Sectoral Indices:- \n\n"
nsecaption += sectoral_df.to_string(col_space=20, justify='center', index = False) + "\n\n"

nsecaption += "FII DII Activity:- \n\n"
nsecaption += fiidii_df.to_string(col_space=20, justify='center', index = False) + "\n\n"

nsecaption += "Calls Open Interest:- \n\n"
nsecaption += ce_df.to_string(col_space=20, justify='center', index = False) + "\n\n"

nsecaption += "Puts Open Interest:- \n\n"
nsecaption += pe_df.to_string(col_space=20, justify='center', index = False) + "\n\n"

# Making the Reddit Post
credentials = 'client_secrets.json'

with open(credentials) as f:
    creds = json.load(f)

reddit = praw.Reddit(client_id=creds['client_id'],
                    client_secret=creds['client_secret'],
                    user_agent=creds['user_agent'],
                    redirect_uri=creds['redirect_uri'],
                    refresh_token=creds['refresh_token'])

subr = 'pythonsandlot'
subreddit = reddit.subreddit(subr)
title = 'Daily Market Recap!'
selftext = nsecaption
subreddit.submit(title,selftext=selftext)