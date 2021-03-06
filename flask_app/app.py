import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

from state_abbrev import us_state_abbrev

app = Flask(__name__)

# app.config.from_object(os.environ['APP_SETTINGS'])
app.config.from_object("config.DevelopmentConfig")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Store(db.Model):
    __tablename__ = 'store'

    name = db.Column(db.String(), primary_key=True)
    storetype = db.Column(db.String(), nullable=False)
    address = db.Column(db.String(), primary_key=True)
    city = db.Column(db.String()) 
    state = db.Column(db.String())
    zipcode = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String())
    website_url = db.Column(db.String())
    logo_url = db.Column(db.String())
    giftcard_url = db.Column(db.String())
    contact_url = db.Column(db.String())
    

    def __init__(self, name, storetype, address, city, state, zipcode, description, website_url, logo_url, giftcard_url, contact_url):
        self.name = name
        self.storetype = storetype
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.description = description
        self.website_url = website_url
        self.logo_url = logo_url
        self.giftcard_url = giftcard_url
        self.contact_url = contact_url

    def __repr__(self):
        return '<name {}>'.format(self.name)
    
    def serialize(self):
        return {
            'name': self.name,
            'storetype': self.storetype,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zipcode': self.zipcode,
            'description': self.description,
            'website_url': self.website_url,
            'logo_url': self.logo_url,
            'giftcard_url': self.giftcard_url,
            'contact_url': self.contact_url
        }

# INSERT INTO store VALUES ('haha','restaurant','Xixi street', 'Needham', 'MA', '02492', 'another place','1.com','12.com','123.com','1234.com');

@app.route("/")
def render_index():
    return render_template('index.html')

@app.route("/index", methods=['GET','POST'])
def render_search():
    if request.args:
        query = request.args['search']
        print(query)
        if query.isnumeric(): # zipcode
            stores = list(Store.query.filter_by(zipcode=query))
        elif len(query) == 2: # state abbrev
            stores = list(Store.query.filter_by(state=query))
        elif query.lower() in us_state_abbrev: # state full name
            stores = list(Store.query.filter_by(state=us_state_abbrev[query.lower()]))
        else:
            stores = list(Store.query.filter_by(city=query))
        if stores:
            show_stores = 1
        else:
            show_stores = 0
        print(show_stores)
        return render_template('index.html', stores=stores, show_stores=show_stores)
    else:
        return render_template('index.html')

@app.route("/about")
def render_about():
    return render_template('about.html')

@app.route("/getall")
def get_all():
    try:
        stores=Store.query.all()
        return  jsonify([e.serialize() for e in stores])
    except Exception as e:
	    return(str(e))

    # to add a store
    # store=Store(
    #             name=name,
    #             ...
    #         )
    #     db.session.add(store)
    #     db.session.commit()

if __name__ == '__main__':
    app.run()