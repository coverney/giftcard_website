'''
This was the original script that uses beautiful soup and try to find
gift card and contact urls from a website. The relevant parts of this code
have been integrated into get_url.py
'''
#
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import numpy as np
from tqdm import tqdm

gift_card_keywords = ['giftcard', 'giftcertificate']
contact_keywords = ['contact', 'findus']
ignored_keywords = ['javascript']
ignored_whole = ['#']

def find_gift_card_url(soup):
    for link in soup.findAll('a'):
        if not link.get('href') or any(keyword in link.get('href') for keyword in ignored_keywords) or any(keyword == link.get('href') for keyword in ignored_whole):
            continue
        string = re.sub(r'\W+', '', str(link)).lower() # only keep alphanumeric characters
        if any(keyword in string for keyword in gift_card_keywords):
            return (link.text, link.get('href'))
    return (np.nan, np.nan)

def find_contact_url(soup):
    for link in soup.findAll('a'):
        string = re.sub(r'\W+', '', str(link)).lower() # only keep alphanumeric characters
        if any(keyword in string for keyword in contact_keywords):
            return (link.text, link.get('href'))
    return (np.nan, np.nan)

if __name__ == "__main__":
    # df_test_urls = pd.read_csv("needham_restaurants.csv")
    #
    # df_test_result = pd.DataFrame(columns=['name', 'website', 'gift_card_txt', 'gift_card_website',
    #     'contact_txt', 'contact_website'])

    df = pd.read_csv("needham_restaurants_url_results.csv")
    df['gift_card_website'] = np.nan
    df['contact_website'] = np.nan
    df['gift_card_txt'] = np.nan
    df['contact_txt'] = np.nan

    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        website = row['website_url']
        if pd.isna(row['website_url']) and pd.isna(row['menu_url']):
            continue
        if pd.isna(row['website_url']):
            website = row['menu_url']
        try:
            r = requests.get(website, headers={"User-Agent":"Chrome/42.0.2311.135"})
            data = r.text
            soup = BeautifulSoup(data, "lxml")
            gift_card_txt, gift_card_website = find_gift_card_url(soup)
            contact_txt, contact_website = find_contact_url(soup)
            df.loc[index, 'gift_card_txt'] = gift_card_txt
            df.loc[index, 'gift_card_website'] = gift_card_website
            df.loc[index, 'contact_website'] = contact_website
            df.loc[index, 'contact_txt'] = contact_txt
        except:
            print('Weird website:', website)

    df.to_csv('needham_restaurants_giftcard_results.csv', index=False)
