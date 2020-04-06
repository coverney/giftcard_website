# Use beautiful soup and try to find gift certificate/ gift card from website and save
# the url
from bs4 import BeautifulSoup
import requests
import re
import pandas as pd

gift_card_keywords = ['giftcard', 'giftcertificate']
contact_keywords = ['contact', 'findus']

def find_gift_card_url(soup):
    for link in soup.findAll('a'):
        string = re.sub(r'\W+', '', str(link)).lower() # only keep alphanumeric characters
        if any(keyword in string for keyword in gift_card_keywords):
            return (link.text, link.get('href'))
    return (None, None)

def find_contact_url(soup):
    for link in soup.findAll('a'):
        string = re.sub(r'\W+', '', str(link)).lower() # only keep alphanumeric characters
        if any(keyword in string for keyword in contact_keywords):
            return (link.text, link.get('href'))
    return (None, None)

if __name__ == "__main__":
    df_test_urls = pd.read_csv("needham_restaurants.csv")

    df_test_result = pd.DataFrame(columns=['name', 'website', 'gift_card_txt', 'gift_card_website',
        'contact_txt', 'contact_website'])

    for index, row in df_test_urls.iterrows():
        website = row['Website']
        name = row['Name']
        r = requests.get(website, headers={"User-Agent":"Chrome/42.0.2311.135"})
        data = r.text
        soup = BeautifulSoup(data, "lxml")
        gift_card_txt, gift_card_website = find_gift_card_url(soup)
        contact_txt, contact_website = find_contact_url(soup)
        df_test_result = df_test_result.append({'name':name, 'website':website, 'gift_card_txt':gift_card_txt,
            'gift_card_website':gift_card_website,
            'contact_txt':contact_txt, 'contact_website':contact_website}, ignore_index = True)
        # if gift_card_website:
        #     print(f'Gift card website: {gift_card_website}')
        # else:
        #     print('No gift card')
        #
        # if contact_website:
        #     print(f'Contact website: {contact_website}')
        # else:
        #     print('No contact')

    df_test_result.to_csv('needham_restaurants_scrape.csv', index=False)
