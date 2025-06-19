from flask import Flask
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def value_or_na(value):
    return "N/A" if str(value) == "-1" else value

def create_app():
    app = Flask(__name__)
    
    with open("config.json", "r", encoding="utf-8") as _config_file:
        config = json.load(_config_file)
        
    app.config['SECRET_KEY'] = config['secret_key']
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///phi_app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.jinja_env.filters['value_or_na'] = value_or_na

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()
        from .utils import create_default_users
        create_default_users()

    return app
