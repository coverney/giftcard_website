from splinter import Browser
from bs4 import BeautifulSoup
import re
import time

if __name__ == "__main__":
    names = []
    addresses = []
    executable_path = {'executable_path':'C:\Program Files\chromedriver.exe'}
    browser = Browser('chrome', **executable_path)
    map_url = "https://www.google.com/maps/search/restaurants+in+needham/@42.292426,-71.24614,14z/data=!3m1!4b1"
    browser.visit(map_url)

    while not browser.is_text_present('Showing results', wait_time=1):
        print('Page not loaded yet')
        pass

    num_iter = 2
    for i in range(num_iter):
        soup = BeautifulSoup(browser.html, "html.parser")
        # get business names
        name_results = soup.find_all('h3', class_="section-result-title")
        for res in name_results:
            names.append(res.get_text())
        # get business addresses
        address_results = soup.find_all('span', class_="section-result-location")
        for res in address_results:
            addresses.append(res.get_text())
        # click the next button
        button = browser.find_by_id("n7lv7yjyC35__section-pagination-button-next")
        button.click()
        time.sleep(1.5)

    print(len(names), names)
    print(len(addresses), addresses)

    browser.quit()
