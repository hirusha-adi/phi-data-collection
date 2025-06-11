from werkzeug.security import generate_password_hash
from .models import User
from . import db

def create_default_users():
    default_users = [
        {'name': 'Administrator', 'username': 'admin', 'password': '12345678'},
        {'name': 'Hirusha Adikari', 'username': 'hirushaadi', 'password': '12345678'},
    ]

    for user in default_users:
        if not User.query.filter_by(username=user['username']).first():
            new_user = User(
                name=user['name'],
                username=user['username'],
                password=generate_password_hash(user['password'])
            )
            db.session.add(new_user)

    db.session.commit()
