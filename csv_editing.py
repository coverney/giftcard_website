'''
This script involves cleaning CSV files. It was used to clean the US population
file and to filter out noisy data from google maps
'''
import pandas as pd
import unidecode
import re
from tqdm import tqdm
import os
import numpy as np

# Keywords we look for by store type
keyword_dict = {'restaurants':['hotel'],
                'book_stores':['book store', 'magazine store', 'game store', 'gift shop',
                    'music store', 'pen store', 'thrift store', 'toy store', 'childrens store',
                    'record store', 'greeting card shop', 'art supply store', 'bookbinder',
                    'books'],
                'florists':['florist', 'flower', 'garden', 'party planner'],
                'clothing_stores':['clothing', 'boutique', 'bridal', 'costume', 'tailor',
                                        'baby store', 'fashion', 'accessories', 'dress',
                                        'formal wear', 'flea market', 'hat shop', 'gift shop',
                                        'lingerie', 'shoe', 'sporting good', 'sportswear',
                                        'thrift store', 't-shirt', 'tuxedo', 'uniform',
                                        'apparel', 'watch store', 'jeweler', 'jewelry',
                                        'wedding', 'swimwear', 'underwear', 'sewing', 'fabric',
                                        'clothes', 'outerwear', 'perfume', 'linen'],
                'beauty_salons':['barber shop', 'spa', 'fitness center', 'hair',
                                        'massage', 'skin care', 'yoga',
                                        'barbershop', 'salon', 'beauty', 'cosmetic',
                                        'makeup', 'eyebrow'],
                'museums':['museum', 'gallery']}

extra_types = {'restaurants':set(), 'book_stores':set(), 'florists':set(),
                'clothing_stores':set(), 'beauty_salons':set(), 'museums':set()}

# Source: https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
def clean_str(str):
    if pd.isna(str):
        return str
    str = re.sub(r"[-()\"#/@;:<>{}`+=~|.!?,]", "", str)
    return unidecode.unidecode(str)

def clean_single_csv(df, filename):
    '''
    Cleans the strings and filters out noisy data based on the store type
    of a single CSV
    '''
    df = df.copy()
    df_new = pd.DataFrame(columns=df.columns)
    df = df.drop_duplicates()
    # remove accented characters
    for index, row in df.iterrows():
        df.loc[index, 'name'] = clean_str(row['name'])
        df.loc[index, 'address'] = clean_str(row['address'])
        df.loc[index, 'type'] = clean_str(row['type'])
    # filter using type specific keywords
    type = [s for s in keyword_dict.keys() if s in filename][0]
    keywords = keyword_dict[type]
    if type == 'restaurants':
        for index, row in df.iterrows():
            if pd.isna(row['type']):
                string = row['name'].lower()
                df.loc[index, 'type'] = type
            else:
                string = row['type'].lower()
            if any(keyword in string for keyword in keywords):
                continue
            df_new = df_new.append(row, ignore_index=True)
    else:
        for index, row in df.iterrows():
            if pd.isna(row['type']):
                string = row['name'].lower()
                df.loc[index, 'type'] = type
            else:
                string = row['type'].lower()
            if any(keyword in string for keyword in keywords):
                df_new = df_new.append(row, ignore_index=True)
            else:
                extra_types[type].add(string)
    return type, df_new

def clean_state_data(state_name, sub_folder_name):
    '''
    Go through all the files for a state, clean them up, and
    add the new dfs to a df representing an entire state and type combo
    '''
    df_dict = {}
    for type in keyword_dict:
        df_dict[type] = pd.DataFrame(columns=['name', 'address', 'type', 'place'])
    path = state_name+'/'+sub_folder_name
    directory = os.fsencode(path)
    for file in tqdm(os.listdir(directory)):
        # Open csv file
        file = file.decode("utf-8")
        # Get place name
        place = np.nan
        lst = file.split('_')[::-1]
        for index, part in enumerate(lst):
            if part == state_name.lower():
                place = ' '.join(lst[index+1:][::-1])
        df_temp = pd.read_csv(path+'/'+file)
        type, df_new = clean_single_csv(df_temp, file)
        df_new['place'] = place
        df_dict[type] = df_dict[type].append(df_new, ignore_index=True)
    # remove duplicates from all the statewide dfs
    for type in df_dict:
        df_dict[type] = df_dict[type].drop_duplicates(subset=df_dict[type].columns.difference(['place']))
        df_dict[type].to_csv(state_name+'/Summary/'+state_name.lower()+'_'+type+'.csv', index=False)
        extra_types[type] = list(extra_types[type])

if __name__ == "__main__":
    clean_state_data('Illinois', 'First Round')
    df_extra = pd.DataFrame(dict([(k,pd.Series(v)) for k,v in extra_types.items()]))
    df_extra.to_csv('Illinois/extra_terms.csv', index=False)

    # some editing done for US_places CSV
    # df = pd.read_csv('US_places_with_pop.csv')
    # df_new = pd.DataFrame(columns=df.columns)
    # for index, row in tqdm(df.iterrows(), total=df.shape[0]):
    #     if 'Balance of' not in row['name']:
    #         if row['name'] == row['state']:
    #             print(f"Special case where place name is same as state name for {row['name']}")
    #             row['name'] = row['name'] + ' ' + row['type']
    #         df_new = df_new.append(row, ignore_index=True)
    # df_new.to_csv('US_places_with_pop.csv', index=False)
