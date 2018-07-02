from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    encoding = db.Column(db.String(1024), index=False, unique=False)

    def __repr__(self):
        return '<User {}> with encoding: {}'.format(self.id, self.encoding)