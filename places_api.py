import requests
import json
import pandas as pd
f = open('api_key.txt', 'r')
api_key = f.read()

def get_places(long, lat, radius, type, filename):
    place_search_request = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={type}&location={long},{lat}&radius={radius}&key={api_key}"
    result = requests.get(place_search_request)
    print(result.status_code)
    with open(filename, 'w') as outfile:
        json.dump(result.json(), outfile)

def get_place_ids(file):
    with open(file) as json_file:
        data = json.load(json_file)
    df = pd.DataFrame(data['results'])
    # return df['place_id'].values
    return df['name'].values


def get_website(place_id):
    # place_details_request = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=website&key={api_key}"
    # result = requests.get(place_details_request)
    # print(result.status_code)
    # result.json()['result']['website']
    with open('fuji.txt') as json_file:
        data = json.load(json_file)
        return data['result']['website']

if __name__ == "__main__":
    long = 42.293934
    lat = -71.264506
    radius = 5000
    type = 'restaurant'
    # place_id = "ChIJQ1EexaaB44kRr9xbss-qudk"
    # print(get_website('fds'))
    print(get_place_ids('needham_restaurants.txt'))
