# Use beautiful soup and try to find gift certificate/ gift card from website and save
# the url
from bs4 import BeautifulSoup
import requests
import re

keywords = ['giftcard', 'giftcertificate']

def find_gift_card_url(soup):
    for link in soup.findAll('a'):
        if not link.string:
            continue
        str = re.sub(r'\W+', '', link.string)
        if str.lower() in keywords:
            return link.get('href')


if __name__ == "__main__":
    test_url = "http://www.fujisteakhouseneedham.com/"
    r = requests.get(test_url)
    data = r.text
    soup = BeautifulSoup(data, "lxml")
    print(find_gift_card_url(soup))
