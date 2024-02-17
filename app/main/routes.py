from flask import render_template, jsonify, url_for, request
from app.main import bp
import uuid

from app import db
from app.main import bp
from app.models import Room

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/create_room', methods=['POST'])
def create_room():
    room_uuid = str(uuid.uuid4())
    room_link = url_for('main.join_room', room_uuid=room_uuid, _external=True)
    room_name = request.form.get('room_name')
    room_description = request.form.get('room_description')

    room = Room(name=room_name, description=room_description, uuid=room_uuid)
    db.session.add(room)
    db.session.commit()

    room_link = url_for('auth.join_room', room_uuid=room_uuid, _external=True)

    return jsonify({'room_uuid': room_uuid, 'room_link': room_link})


def join_room(room_uuid):
    return render_template("join_room.html", room_uuid=room_uuid)