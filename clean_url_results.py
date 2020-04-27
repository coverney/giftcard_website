'''
This script cleans the results from scrapping website, giftcard, and contact urls
It splits the CSV from get_url.py into two CSVs df_searched and df_notsearched,
and further separates df_searched into a list of businesses with giftcard urls
and a list of businesses with contact urls but no giftcard urls. We also remove
duplicates, chain stores, and invalid rows.
'''
import pandas as pd
import re
from tqdm import tqdm
import numpy as np

unwanted_url_keywords = ['find-a-store', 'stores', 'shops', 'store-details',
                        'locator', 'locate', 'pages', '/shop/', 'outlets', '/store/', 'location']

common_url_starts = ['sites.google.com']

def clean_url_regex(reference_url, url):
    '''
    A regex pattern matching approach to turn a relative url into an absolute one
    '''
    m = re.search(r'^http[s]?://', url)
    if m is not None: # url is already absolute so just return
        return url
    # get part of reference_url until .[com]/
    m = re.search(r'^(http[s]?)://([w]{3}.)?([\w-]*).([a-z.]*)/', reference_url)
    if m is not None:
        url_head = m.group(0)
        if url.startswith('/'):
            return url_head+url[1:]
        else:
            return url_head+url
    else:
        print(f"Weird reference url, {reference_url}")

def clean_url(reference_url, url):
    '''
    A python string manipulation approach to turn a relative url into an absolute one
    '''
    if url.startswith('http') or url.startswith('//'): # url is already absolute so just return
        return url
    # get part of reference_url until .[com]/
    url_head = '/'.join(reference_url.split('/')[:3])+'/'
    if url.startswith('/'):
        return url_head+url[1:]
    else:
        return url_head+url

def clean_df(df, store_type):
    '''
    Separate address into state, zipcode, and city/town.
    Also deal with relative and absolute links.
    Example: 793 Iyannough Rd, Hyannis, MA 02601
    Only run on results with giftcard urls/ contact urls
    '''
    df = df.copy()
    df['state'] = np.nan
    df['zipcode'] = np.nan
    df['store_type'] = store_type
    for index, row in  tqdm(df.iterrows(), total=df.shape[0]):
        # split up address
        address = row['address']
        if pd.isna(address):
            continue
        m = re.search(r', ([\w ]*[^\W_][\w ]*), ([A-Z]{2}) (\d{5})$', address)
        if m is not None:
            relevant_part = m.group(0)
            place = relevant_part.split(', ')[1]
            state = relevant_part.split(', ')[-1].split(' ')[0]
            zipcode = relevant_part.split(', ')[-1].split(' ')[1]
            df.loc[index, 'state'] = state
            df.loc[index, 'zipcode'] = zipcode
            df.loc[index, 'place'] = place
        else:
            df.loc[index, 'address'] = np.nan
            continue
        # deal with relative links
        website = row['website_url']
        if pd.isna(website):
            if pd.isna(row['menu_url']):
                df.loc[index, 'address'] = np.nan
                continue
            df.loc[index, 'website_url'] = row['menu_url']
            website = row['menu_url']
        if (any(keyword in website.lower() for keyword in unwanted_url_keywords) or
                (not pd.isna(row['description']) and 'chain' in row['description'].lower())):
            df.loc[index, 'address'] = np.nan # probably a chain store
            continue
        if not any(keyword in website.lower() for keyword in common_url_starts):
            df.loc[index, 'website_url'] = '/'.join(website.split('/')[:3])+'/'
        if not pd.isna(row['gift_card_website']):
            df.loc[index, 'gift_card_website'] = clean_url(website, row['gift_card_website'])
        if not pd.isna(row['contact_website']):
            df.loc[index, 'contact_website'] = clean_url(website, row['contact_website'])
    return df[df['address'].notna()].drop_duplicates(subset='website_url', keep=False).drop_duplicates(subset='name', keep=False)

def has_zipcode(address, state_initials=''):
    '''
    Determines whether an address has a zipcode or not, which is a sign that
    a particular row has been searched
    '''
    if address.isdigit():
        return False
    m = re.search(r', ([A-Z]{2}) (\d{5})$', address)
    # m = re.search(r'\d{5}$', address)
    if m is not None:
        zip = m.group(0)
        # if address.endswith(', '+state_initials+' '+zip):
        #     return True
        return True
    return False

def create_sub_dfs(df, store_type):
    '''
    Create df_giftcard and df_contact from df_searched
    '''
    df_giftcard = df[df['gift_card_website'].notna()]
    df_contact = df[(df['gift_card_website'].isna()) & (df['contact_website'].notna())]
    return clean_df(df_giftcard, store_type), clean_df(df_contact, store_type)

def filter_via_zipcode(df, state_initials=''):
    '''
    Create df_searched and df_notsearched based on zipcode
    '''
    df_grouped = df.groupby(by='place')
    dataframes = [group for _, group in df_grouped]
    df_searched = pd.DataFrame(columns=df.columns)
    df_notsearched = pd.DataFrame(columns=df.columns)
    for df_place in tqdm(dataframes[:]):
        # reverse rows and find index of first one with zip code
        end_index = -1
        for index, row in df_place[::-1].iterrows():
            if pd.isna(row['address']):
                continue
            if has_zipcode(row['address'], state_initials):
                end_index = index
                break
        df_searched = df_searched.append(df_place.loc[:end_index], ignore_index=True)
        df_notsearched = df_notsearched.append(df_place.loc[end_index+1:], ignore_index=True)
    return df_searched, df_notsearched

def filter_via_searchedcol(df):
    '''
    Create df_searched and df_notsearched based on the value of the
    searched column
    '''
    df_searched = df[df['searched']==1]
    df_notsearched = df[df['searched']==0]
    return df_searched, df_notsearched

if __name__ == "__main__":
    # reference_url = 'https://www.curransflowers.com/' # 'https://www.curransflowers.com/'
    # url = '/gifts/gift-cards/'
    # print(clean_url(reference_url, url))

    # m = re.search(r', ([\w ]*[^\W_][\w ]*), ([A-Z]{2}) (\d{5})$', '793 Iyannough Rd, Hyannis, MA 02601')
    # if m is not None:
    #     relevant_part = m.group(0)
    #     place = relevant_part.split(', ')[1]
    #     state = relevant_part.split(', ')[-1].split(' ')[0]
    #     zipcode = relevant_part.split(', ')[-1].split(' ')[1]
    #     print(place, state, zipcode)

    # df = pd.read_csv('Massachusetts/massachusetts_clothing_stores_url_results.csv')
    # df_searched, df_notsearched = filter_via_searchedcol(df)
    # df_searched.to_csv('Massachusetts/massachusetts_clothing_stores_url_results_rnd1.csv', index=False)
    # df_notsearched.to_csv('Massachusetts/massachusetts_clothing_stores_url_results_rnd2.csv', index=False)

    df_searched = pd.read_csv('Massachusetts/massachusetts_restaurants_url_results_rnd1.csv')
    df_giftcard, df_contact = create_sub_dfs(df_searched, 'restaurant')
    df_giftcard.to_csv('Massachusetts/massachusetts_restaurants_giftcard_results_rnd1.csv', index=False)
    df_contact.to_csv('Massachusetts/massachusetts_restaurants_contact_results_rnd1.csv', index=False)
