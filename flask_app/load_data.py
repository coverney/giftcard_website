import os
import pandas as pd
import argparse
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import psycopg2

from app import Store

def clean_unicode(text):
    if type(text) == str:
        return text.encode('ascii', 'ignore').decode('ascii')
    return ''

def store_exist(session, name, address):
    return session.query(Store.name).filter_by(name=name, address=address).scalar()

def format_zipcode(zipcode):
    zipcode = str(zipcode)
    while len(zipcode) < 5:
        zipcode = "0" + zipcode
    return zipcode

if __name__=="__main__":
    # load foldername
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', action="store", dest="foldername")
    inputs = parser.parse_args()

    filenames = os.listdir(inputs.foldername)
    giftcard_csvs = []
    for filename in filenames:
        if 'giftcard' in filename:
            giftcard_csvs.append(f'{inputs.foldername}{filename}')
    
    db_string = "postgresql:///giftcard_website"
    db = create_engine(db_string, convert_unicode=True)
    Session = sessionmaker(db)
    session = Session()
    
    insert_count = 0

    for giftcard_csv in giftcard_csvs:
        giftcard_df = pd.read_csv(giftcard_csv)
        for index, row in giftcard_df.iterrows():
            new_store = Store(
                name = row['name'],
                storetype = row['store_type'],
                address = clean_unicode(row['address']),
                city = row['place'],
                state = row['state'],
                zipcode = format_zipcode(row['zipcode']),
                description = clean_unicode(row['description']),
                website_url = clean_unicode(row['website_url']),
                logo_url = '',
                giftcard_url = clean_unicode(row['gift_card_website']),
                contact_url = clean_unicode(row['contact_website'])
            )
            # only add row if store doesn't exist already
            if not store_exist(session, new_store.name, new_store.address):
                session.add(new_store)
                session.commit()

            insert_count += 1
            if insert_count % 100 == 0:
                print(f'{insert_count} rows processed.')

            
