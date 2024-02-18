from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()

login_manager = LoginManager()
login_manager.login_view='auth.login'
login_manager.login_message_category='info'
