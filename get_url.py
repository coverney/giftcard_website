from splinter import Browser
from bs4 import BeautifulSoup
import re

if __name__ == "__main__":
    executable_path = {'executable_path':'C:\Program Files\chromedriver.exe'}
    browser = Browser('chrome', **executable_path)
    google = "https://www.google.com/"
    search_term = "fuji steakhouse needham"
    browser.visit(google)
    browser.fill("q", search_term)
    button = browser.find_by_name("btnK")
    button.click()

    while not browser.is_text_present('results', wait_time=1):
        print('Search not complete yet')
        pass

    # ALSO NEED TO EXTRACT MENU URL
    soup = BeautifulSoup(browser.html, "html.parser")
    urls = soup.find_all('a', href=True, text=re.compile("Website"))
    if len(urls) > 1:
        print("found multiple website urls")
    for a in urls:
        print(a['href'])

    browser.quit()
