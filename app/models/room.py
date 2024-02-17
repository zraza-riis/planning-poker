from app.extensions import db
from datetime import datetime

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Room {self.name}>'
    
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    room = db.relationship('Room', backref=db.backref('estimations', lazy=True))

    def __repr__(self):
        return f'<User {self.name}>'

class Estimation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('estimations', lazy=True))
    room = db.relationship('Room', backref=db.backref('estimations', lazy=True))

    def __repr__(self):
        return f'<Estimation {self.value}>'
