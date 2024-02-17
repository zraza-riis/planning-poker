from flask import render_template, jsonify, url_for, request, redirect
from flask_socketio import emit, join_room, leave_room
from app.main import bp
import uuid

from app import db, socketio
from app.main import bp
from app.models import Room, Player, Prompt

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
        join_link = url_for('main.join_room', room_uuid=room_uuid, _external=True)

        room = Room(name=room_name, description=room_description, uuid=room_uuid, join_link=join_link)
        db.session.add(room)
        db.session.commit()

        socketio.emit('new_room', {'room_uuid': room_uuid}, namespace='/')

        return redirect(join_link)
    return render_template('create_room.html')

@bp.route('/join/<room_uuid>', methods=['GET', 'POST'])
def join_room(room_uuid):
    room = Room.query.filter_by(uuid=room_uuid).first_or_404()
    if request.method == 'POST':
        display_name = request.form.get('display_name')

        player = Player(name=display_name, room=room)
        db.session.add(player)
        db.session.commit()

        return redirect(url_for('main.room_page', room_uuid=room_uuid))
    return render_template("join_room.html", room=room)

@socketio.on('connect', namespace='/')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('new_prompt', namespace='/')
def handle_new_prompt(data):
    room_uuid = data['room_uuid']
    prompt_title = data['prompt_title']

    print(f"Received new_prompt in room {room_uuid}: {prompt_title}")

    room = Room.query.filter_by(uuid=room_uuid).first_or_404()

    new_prompt = Prompt(title=prompt_title)
    db.session.add(new_prompt)
    db.session.commit()

    socketio.emit('new_prompt', {'prompt_title': prompt_title}, namespace='/')

@bp.route('/room/<room_uuid>', methods=['GET'])
def room_page(room_uuid):
    room = Room.query.filter_by(uuid=room_uuid).first_or_404()
    print(room)

    join_room(room_uuid)

    return render_template('room.html', room=room)
