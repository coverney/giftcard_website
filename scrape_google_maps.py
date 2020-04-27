'''
This script is used to scrape google maps. We basically get the first few results
of a certain type of business among the most populated places in a state
'''
from splinter import Browser
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

executable_path = {'executable_path':'C:\Program Files\chromedriver.exe'}
browser = Browser('chrome', **executable_path)
memo = set()

def scrape_google_maps(type, search_term, filename):
    '''
    Scrape google maps based on a search term and save the results as a CSV file
    '''
    if search_term in memo:
        # print(f"Duplicate search term: {search_term}")
        return
    else:
        memo.add(search_term)
    names = []
    addresses = []
    types = []
    google_maps_url = "http://maps.google.com/"
    browser.visit(google_maps_url)
    while not browser.is_text_present("Coronavirus (COVID-19)", wait_time=1):
        # print('Page not loaded yet')
        pass
    browser.fill("q", search_term+'\n')
    while not browser.is_text_present('Showing results', wait_time=1) and not browser.is_text_present('Directions', wait_time=1) and not browser.is_text_present('Don\'t see what you\'re looking for?', wait_time=1):
        # print('Page not loaded yet')
        pass
    # scrape google map results
    if type in ['restaurants', 'florists', 'beauty salons']:
        try:
            while(True):
                soup = BeautifulSoup(browser.html, "html.parser")
                # get business names
                name_results = soup.find_all('h3', class_="section-result-title")
                for res in name_results:
                    names.append(res.get_text())
                # get business addresses
                address_results = soup.find_all('span', class_="section-result-location")
                for res in address_results:
                    addresses.append(res.get_text())
                # get business type
                type_results = soup.find_all('span', class_="section-result-details")
                for res in type_results:
                    types.append(res.get_text())
                # click the next button
                button = browser.find_by_id("n7lv7yjyC35__section-pagination-button-next")
                button.click()
                time.sleep(2)
        except:
            pass
    else: # just get first 5 pages
        num_iters = 5
        try:
            for i in range(num_iters):
                soup = BeautifulSoup(browser.html, "html.parser")
                # get business names
                name_results = soup.find_all('h3', class_="section-result-title")
                for res in name_results:
                    names.append(res.get_text())
                # get business addresses
                address_results = soup.find_all('span', class_="section-result-location")
                for res in address_results:
                    addresses.append(res.get_text())
                # get business type
                type_results = soup.find_all('span', class_="section-result-details")
                for res in type_results:
                    types.append(res.get_text())
                # click the next button
                button = browser.find_by_id("n7lv7yjyC35__section-pagination-button-next")
                button.click()
                time.sleep(2)
        except:
            pass

    # print(f'Num results for {search_term} is {len(names)}')
    if len(names) > 0:
        # save names and addresses to CSV
        pd.DataFrame(list(zip(names, addresses, types)),
                        columns=['name', 'address', 'type']).to_csv(filename, index=False)
    else:
        print(f'No results for {search_term}')


# go through list of US cities and towns and actively type them into google maps
# the query should have format "type in city/town, STATE" (name of input is "q", id = "searchboxinput")
# from there scrape the names, addresses, and types

if __name__ == "__main__":
    # read in US place data
    df_places = pd.read_csv('US_places_with_pop.csv')
    df_ca = df_places[df_places.state == 'California']
    threshold1 = df_ca['population'].quantile(0.75)
    threshold2 = df_ca['population'].quantile(0.5)
    print('Initial size:', df_ca.shape)
    print('Percentiles of population:', threshold2, threshold1)
    df_ca_sub = df_ca[(df_ca.population >= threshold2) & (df_ca.population < threshold1)]
    print('Reduced size:', df_ca_sub.shape)
    # print('First place:', df_ca_sub.iloc[0])
    print('Last place:', df_ca_sub.iloc[-1])

    # read in google places API types
    df_types = pd.read_csv('google_place_types2.csv')
    for index, row in df_ca_sub.iloc[:].iterrows():
        for type in df_types['type'].values[:]:
            search_term = f"{type} in {row['name']}, {row['state']}"
            filename = f"{row['state']}/{row['name'].replace(' ', '_').lower()}_{row['state'].lower()}_{type.replace(' ', '_')}.csv"
            scrape_google_maps(type, search_term, filename)

    browser.quit()
