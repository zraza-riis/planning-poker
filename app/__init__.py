from flask import Flask
from flask_cors import CORS

from config import Config
from app.extensions import db, login_manager, socketio

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize Flask extensions here
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # Register blueprints here
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.ui import bp as ui_bp
    app.register_blueprint(ui_bp)

    CORS(app)

    @app.route('/test/')
    def test_page():
        return '<h1>It Works!</h1>'

    return app