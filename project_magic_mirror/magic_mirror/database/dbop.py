from app import db
from database import models
import json

def add_user(enc):
    encoding_str = json.dumps(enc)
    u = models.User(encoding = encoding_str)
    db.session.add(u)
    db.session.commit()
    return u.id

def get_user_encoding(id):
    u = models.User.query.get(id)
    return json.loads(u.encoding)


def get_all_user():
    users = models.User.query.all()
    all_users = {}
    for u in users:
        all_users[u.id] = json.loads(u.encoding)
    return all_users