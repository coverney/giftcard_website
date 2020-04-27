from app import db

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