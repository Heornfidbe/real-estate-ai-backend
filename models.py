from database import db
from datetime import datetime

class PropertyListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(20))
    title = db.Column(db.String(200))
    region = db.Column(db.String(100))
    bhk = db.Column(db.Integer)
    area = db.Column(db.Float)
    price = db.Column(db.Float)
    description = db.Column(db.Text)
    image_filename = db.Column(db.String(200))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "owner_name": self.owner_name,
            "contact": self.contact,
            "title": self.title,
            "region": self.region,
            "bhk": self.bhk,
            "area": self.area,
            "price": self.price,
            "description": self.description,
            "image": self.image_filename,
            "date_added": self.date_added.isoformat()
        }
