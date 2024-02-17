from flask import render_template
from app.ui import bp

@bp.route('/ui/room/create')
def new_game():
    return render_template('create_room.html')

@bp.route('/ui/room/join')
def join_game():
    return render_template('join_room.html')
