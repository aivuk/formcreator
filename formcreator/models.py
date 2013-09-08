import sha
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, email='', is_admin=False):
        self.username = username
        self.password = sha.new(password).hexdigest()
        self.email = email
        self.is_admin = is_admin

    def __repr__(self):
        return '<User %r>' % self.username

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id
