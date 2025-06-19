from werkzeug.security import generate_password_hash
from .models import User, Area
from . import db
import json

def create_default_users():
    with open("config.json", "r", encoding="utf-8") as _config_file:
        config = json.load(_config_file)
    default_users = config['default_users']
    
    default_areas = config['default_areas']

    for user in default_users:
        if not User.query.filter_by(username=user['username']).first():
            new_user = User(
                name=user['name'],
                username=user['username'],
                password=generate_password_hash(user['password'])
            )
            db.session.add(new_user)

    for area in default_areas:
        if not Area.query.filter_by(name=area['name']).first():
            new_area = Area(name=area['name'])
            db.session.add(new_area)

    db.session.commit()
