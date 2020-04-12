import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Store(db.Model):
    __tablename__ = 'store'

    name = db.Column(db.String(), primary_key=True)
    storetype = db.Column(db.String())
    giftcard = db.Column(db.String())
    contact = db.Column(db.String())

    def __init__(self, name, storetype, giftcard, contact):
        self.name = name
        self.storetype = storetype
        self.giftcard = giftcard
        self.contact = contact

    def __repr__(self):
        return '<name {}>'.format(self.name)
    
    def serialize(self):
        return {
            'name': self.name,
            'storetype': self.storetype,
            'giftcard': self.giftcard,
            'contact': self.contact
        }

@app.route("/")
def hello():
    return "Hello World!"

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