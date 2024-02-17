from flask import render_template, jsonify, url_for, request, redirect
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

@bp.route('/create-room', methods=['GET', 'POST'])
def create_room():
    if request.method == 'POST':
        room_uuid = str(uuid.uuid4())
        room_name = request.form.get('room_name')
        room_description = request.form.get('room_description')

        room = Room(name=room_name, description=room_description, uuid=room_uuid)
        db.session.add(room)
        db.session.commit()
        return redirect(url_for('main.join_room', room_uuid=room_uuid))
    return render_template('create_room.html')

@bp.route('/join/<room_uuid>', methods=['GET', 'POST'])
def join_room(room_uuid):
    room = Room.query.filter_by(uuid=room_uuid).first_or_404()
    if request.method == 'POST':
        display_name = request.form.get('display_name')
        return redirect(url_for('main.room_page', room_uuid=room_uuid))
    return render_template("join_room.html", room=room)

@bp.route('/room/<room_uuid>', methods=['GET'])
def room_page(room_uuid):
    room = Room.query.filter_by(uuid=room_uuid).first_or_404()
    print(room)
    return render_template('room.html', room=room)
