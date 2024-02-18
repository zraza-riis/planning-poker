from flask import render_template, jsonify, url_for, request, redirect, session
from flask_socketio import emit, join_room, leave_room
from app.main import bp
import uuid

from app import db, socketio
from app.main import bp
from app.models import Room, Player, Prompt, Estimation

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

        session['player_name'] = display_name

        return redirect(url_for('main.room_page', room_uuid=room_uuid))
    return render_template("join_room.html", room=room)

@bp.route('/room/<room_uuid>', methods=['GET'])
def room_page(room_uuid):
    room = Room.query.filter_by(uuid=room_uuid).first_or_404()

    join_room(room_uuid)

    return render_template('room.html', room=room)

@socketio.on('connect', namespace='/')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect', namespace='/')
def handle_disconnect():
    print('Client disconnected')
    
@socketio.on('join_room', namespace='/')
def handle_join_room(data):
    room_uuid = data['room_uuid']
    player_name = session.get('player_name', 'Anonymous')

    room = Room.query.filter_by(uuid=room_uuid).first_or_404()

    player = Player.query.filter_by(name=player_name, room=room).first_or_404()
    db.session.add(player)
    db.session.commit()

    socketio.emit('player_joined', {'player_name': player_name, 'players': get_connected_players(room_uuid)}, namespace='/')

@socketio.on('leave_room', namespace='/')
def handle_leave_room(data):
    room_uuid = data['room_uuid']
    player_name = session.get('player_name', 'Anonymous')

    room = Room.query.filter_by(uuid=room_uuid).first_or_404()

    player = Player.query.filter_by(name=player_name, room=room).first()
    if player:
        db.session.delete(player)
        db.session.commit()

    socketio.emit('player_left', {'player_name': player_name, 'players': get_connected_players(room_uuid)}, namespace='/')

def get_connected_players(room_uuid):
    room = Room.query.filter_by(uuid=room_uuid).first()
    if room:
        return [player.name for player in room.players]
    return []

@socketio.on('new_prompt', namespace='/')
def handle_new_prompt(data):
    room_uuid = data['room_uuid']
    prompt_title = data['prompt_title']
    prompt_description = data['prompt_description']

    print(f"Received new_prompt in room {room_uuid}: {prompt_title} {prompt_description}")

    room = Room.query.filter_by(uuid=room_uuid).first_or_404()

    new_prompt = Prompt(title=prompt_title, description=prompt_description)
    db.session.add(new_prompt)
    db.session.commit()

    socketio.emit('new_prompt', {'prompt_id': new_prompt.id, 'prompt_title': prompt_title, 'prompt_description': prompt_description}, namespace='/')

@socketio.on('new_active_prompt', namespace='/')
def handle_new_active_prompt(data):
    room_uuid = data['room_uuid']
    prompt_id = data['prompt_id']

    room = Room.query.filter_by(uuid=room_uuid).first_or_404()
    prompt = Prompt.query.get(prompt_id)

    if room and prompt:
        room.active_prompt_id = prompt.id
        db.session.commit()

        socketio.emit('active_prompt_changed', {'prompt_id': prompt_id, 'prompt_title': prompt.title, 'prompt_description': prompt.description}, namespace='/')
    else:
        print("Room or Prompt not found.")

def get_estimations_for_active_prompt(room_uuid):
    room = Room.query.filter_by(uuid=room_uuid).first()

    if room and room.active_prompt_id:
        estimations = Estimation.query.filter_by(room_id=room.id, prompt_id=room.active_prompt_id).all()
        estimations_dict = {estimation.player.name: estimation.value for estimation in estimations}
        return estimations_dict

    return {}

@socketio.on('new_estimation_submitted', namespace='/')
def handle_new_estimation(data):
    room_uuid = data['room_uuid']
    estimation_value = data['estimation_value']
    player_name = session.get('player_name', 'Anonymous')

    room = Room.query.filter_by(uuid=room_uuid).first_or_404()
    prompt_id = room.active_prompt_id

    if room and prompt_id:
        new_estimation = Estimation(value=estimation_value, player_name=player_name, room=room, prompt_id=prompt_id)
        db.session.add(new_estimation)
        db.session.commit()

        estimations_dict = get_estimations_for_active_prompt(room_uuid)

        socketio.emit('new_estimation', {'player_name': player_name, 'estimation_value': estimation_value, 'estimations': estimations_dict}, namespace='/')
    else:
        print("Room or Prompt not found.")




