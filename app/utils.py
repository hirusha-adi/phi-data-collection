from werkzeug.security import generate_password_hash
from .models import User, Area
from . import db

def create_default_users():
    default_users = [
        {'name': 'Administrator', 'username': 'admin', 'password': '12345678'},
        {'name': 'Hirusha Adikari', 'username': 'hirushaadi', 'password': '12345678'},
    ]
    
    default_areas = [
        {'name': 'Ambanpola'},
        {'name': 'Abakolawewa'},
        {'name': 'Keththaphuwa'},
        {'name': 'Borawewa'},
    ]

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
