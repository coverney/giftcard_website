'''
This script takes the results from google maps and gets the business information
using google search features. If a business has a local website, then we use
BeautifulSoup to scrape the website and look for gift card and contact info links
'''
from splinter import Browser
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
import requests

executable_path = {'executable_path':'C:\Program Files\chromedriver.exe'}
browser = Browser('chrome', **executable_path)
types = ['restaurants', 'book_stores', 'florists',
                'clothing_stores', 'beauty_salons', 'museums']

gift_card_keywords = ['giftcard', 'giftcertificate']
contact_keywords = ['contact', 'findus']
ignored_keywords = ['javascript']
ignored_whole = ['#']

def find_gift_card_url(soup):
    '''
    Looks at a website's HTML and tries to find a gift card url
    '''
    for link in soup.findAll('a'):
        if not link.get('href') or any(keyword in link.get('href') for keyword in ignored_keywords) or any(keyword == link.get('href') for keyword in ignored_whole):
            continue
        string = re.sub(r'\W+', '', str(link)).lower() # only keep alphanumeric characters
        if any(keyword in string for keyword in gift_card_keywords):
            return (link.text, link.get('href'))
    return (np.nan, np.nan)

def find_contact_url(soup):
    '''
    Looks at a website's HTML and tries to find a contact us url
    '''
    for link in soup.findAll('a'):
        string = re.sub(r'\W+', '', str(link)).lower() # only keep alphanumeric characters
        if any(keyword in string for keyword in contact_keywords):
            return (link.text, link.get('href'))
    return (np.nan, np.nan)

def get_website_urls(html):
    '''
    From a google search result of a local business, we try to extract
    the website url, address, and description
    '''
    main_url = np.nan
    menu_url = np.nan
    address = np.nan
    description = np.nan
    soup = BeautifulSoup(html, "html.parser")
    main_urls = soup.find_all('a', href=True, text=re.compile("Website"))
    if len(main_urls) > 1:
        print("found multiple website urls, saving the first one")
    for a in main_urls[:1]:
        main_url = a['href']
    # Get the menu url
    span = soup.find_all('span', text=re.compile("Menu:"))
    if len(span) > 0:
        menu_urls = span[0].parent.find_all('a', href=True)
        if len(menu_urls) > 1:
            print("found multiple menu urls, saving the first one")
        for a in menu_urls[:1]:
            menu_url = a['href']
    # Get the address
    address_urls = soup.find_all('a', href=True, text=re.compile("Address"))
    if len(address_urls) > 0:
        if len(address_urls) > 1:
            print("found multiple address urls, using the first one")
        address = address_urls[0].parent.find_next('span').text
    # Get the description
    spans = soup.find_all('span', {'class': 'ggV7z'})
    for span in spans:
        if span.parent.name == 'div' and span.parent.has_attr('class') and span.parent['class'][0] == 'k2VFwd':
            description = span.text
    return main_url, menu_url, address, description

def search(browser, search_term):
    '''
    Enter a search term into google search and get the html of the results page
    '''
    google = "https://www.google.com/"
    browser.visit(google)
    browser.fill("q", search_term+'\n')
    while not browser.is_text_present('results', wait_time=1) and not browser.is_text_present('did not match any documents.', wait_time=1):
        # print('Search not complete yet')
        pass
    return get_website_urls(browser.html)

def search_one_csv(df, state_name, start, end):
    '''
    Keep scrapping google map results in a single CSV file until 5 businesses
    with gift card urls are found for a single town/city. Usually we run this
    function for different dataframe ranges because it takes a long time
    '''
    if start == 0:
        df['description'] = np.nan
        df['website_url'] = np.nan
        df['menu_url'] = np.nan
        df['gift_card_website'] = np.nan
        df['contact_website'] = np.nan
        df['gift_card_txt'] = np.nan
        df['contact_txt'] = np.nan
        df['searched'] = 0
    df_grouped = df.groupby(by='place')
    dataframes = [group for _, group in df_grouped]
    for df_place in dataframes[start:end]: # 235
        counter = 0
        for index, row in df_place.iterrows():
            if counter > 5:
                break
            if pd.isna(row['address']):
                search_term = f"{row['name']} {row['type']} in {row['place']}, {state_name}"
                res = search(browser, search_term)
            else:
                search_term = f"{row['name']} {row['type']} in {row['address']}, {state_name}"
                res = search(browser, search_term)
                # if no results obtained, try with more general search term
                if pd.isna(res[0]) and pd.isna(res[1]) and pd.isna(res[2]) and pd.isna(res[3]):
                    search_term = f"{row['name']} {row['type']} in {row['place']}, {state_name}"
                    res = search(browser, search_term)
            # if there is a website url then try to get the giftcard url
            df.loc[index, 'website_url'] = res[0]
            df.loc[index, 'menu_url'] = res[1]
            df.loc[index, 'address'] = res[2]
            df.loc[index, 'description'] = res[3]
            df.loc[index, 'searched'] = 1
            website = res[0]
            if pd.isna(res[0]) and pd.isna(res[1]):
                continue
            if pd.isna(res[0]):
                website = res[1]
            try:
                # print(row['name'], website)
                if not pd.isna(website) and website.startswith('http') and not website.startswith('.pdf'):
                    r = requests.get(website, headers={"User-Agent":"Chrome/42.0.2311.135"}, timeout=10)
                    data = r.text
                    soup = BeautifulSoup(data, "lxml")
                    gift_card_txt, gift_card_website = find_gift_card_url(soup)
                    contact_txt, contact_website = find_contact_url(soup)
                    if not pd.isna(gift_card_website):
                        counter += 1
                    df.loc[index, 'gift_card_txt'] = gift_card_txt
                    df.loc[index, 'gift_card_website'] = gift_card_website
                    df.loc[index, 'contact_website'] = contact_website
                    df.loc[index, 'contact_txt'] = contact_txt
                else:
                    raise Exception('not a valid url?')
            except Exception as e:
                print(f"Weird website:{website} with error {e}")
    return df

def search_state(state_name):
    '''
    Completes and combines the scrapping results for an entire state. This
    function is not used because it takes such a long time to scrape everything
    '''
    df_state = pd.DataFrame(columns=['name', 'address', 'type', 'place', 'description', 'website_url', 'menu_url'])
    path = state_name+'/Summary'
    directory = os.fsencode(path)
    for file in tqdm(os.listdir(directory)):
        # Open csv file
        file = file.decode("utf-8")
        df_temp = pd.read_csv(path+'/'+file)
        df_new = search_one_csv(df_temp)
        df_state = df_state.append(df_new, ignore_index=True)
    df_state = df_state.drop_duplicates(subset=['name', 'address', 'type'])
    df_state.to_csv(state_name+'/'+state_name.lower()+'_url_results.csv', index=False)


if __name__ == "__main__":
    # search_term_test = "fuji steakhouse needham"
    # search_term_test = "Jumbo Chinese in 191 NY59, New York"
    # print(search(browser, search_term_test))

    # didn't finish museum for MA on group 2
    state_name = 'New York'
    store_type = 'restaurants'
    round_num = 1
    start = 100
    end = 200

    # df_old = pd.read_csv(state_name+'/'+state_name.lower()+'_beauty_salons_url_results_rnd1.csv')
    if start == 0:
        df = pd.read_csv(f"{state_name}/Summary/{state_name.lower()}_{store_type}.csv")
    else:
        df = pd.read_csv(f"{state_name}/{state_name.lower()}_{store_type}_url_results_rnd{round_num}.csv")

    for i in tqdm(range(start, end)):
        try:
            df = search_one_csv(df, state_name, i, i+1)
        except Exception as e:
            print(f"ended on {i} with error {e}")
            break
    
    print("Saving to csv now")
    df.to_csv(f"{state_name}/{state_name.lower()}_{store_type}_url_results_rnd{round_num}.csv", index=False)
    browser.quit()
