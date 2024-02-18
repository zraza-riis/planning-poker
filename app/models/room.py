from app.extensions import db
from datetime import datetime

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    join_link = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    active_prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'))
    active_prompt = db.relationship('Prompt', foreign_keys=[active_prompt_id], backref='active_in_room', uselist=False)

    def __repr__(self):
        return f'<Room {self.name}>'
    
class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    room = db.relationship('Room', backref=db.backref('players', lazy=True))

    def __repr__(self):
        return f'<Player {self.name}>'

class Estimation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)

    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompt.id'), nullable=False)

    player = db.relationship('Player', backref=db.backref('estimations', lazy=True))
    room = db.relationship('Room', backref=db.backref('estimations', lazy=True))
    prompt = db.relationship('Prompt', back_populates='estimations')

    def __repr__(self):
        return f'<Estimation {self.value}>'
    
class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(248), nullable=False)
    description = db.Column(db.String(512), nullable=True)

    estimations = db.relationship('Estimation', back_populates='prompt', foreign_keys='Estimation.prompt_id', lazy=True)

    def __repr__(self):
        return f'<Prompt {self.title}>'
