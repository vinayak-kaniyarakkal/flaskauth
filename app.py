import json
import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime

TOKEN_LIFE = 30 * 60

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Th1s1ss3cr3t'
if os.environ.get('IS_TEST') == 'True':
    app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///testdb.sqlite3')
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = ('sqlite:///db.sqlite3')
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(50))

    @staticmethod
    def get_user_by_name(name):
        return User.query.filter_by(name=name).first()

    @staticmethod
    def create_user(data):
        hashed_password = generate_password_hash(
            data['password'], method='sha256')
        new_user = User(
            id=uuid.uuid4().hex, name=data['name'], password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

    def get_token(self):
        now = datetime.datetime.now()
        expiry = now + datetime.timedelta(seconds=TOKEN_LIFE)
        token = jwt.encode(
            {'id': self.id, 'expiry': expiry.strftime("%m/%d/%Y, %H:%M:%S")},
            app.config['SECRET_KEY'])
        return token.decode('UTF-8')

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<User: %s>' % str(self)


class LogMixin(db.Model):
    __abstract__ = True

    id = db.Column(db.String(50), primary_key=True)
    time = db.Column(db.String(50), default=datetime.datetime.now)

    def __str__(self):
        return '%s: %s' % (self.time, str(self.user_id))

    def __repr__(self):
        return '<%s: %s>' % (type(self).__name__, str(self))

    @classmethod
    def log(cls, **kwargs):
        access_log = cls(id=uuid.uuid4().hex, **kwargs)
        db.session.add(access_log)
        db.session.commit()


class ValidLogin(LogMixin):
    user_id = db.Column(db.String(50))


class InvalidLogin(LogMixin):
    user_id = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(50), nullable=True)


@app.route('/register', methods=['POST'])
def signup_user():
    data = request.get_json() or request.form
    User.create_user(data)
    return jsonify({'message': 'registered successfully'})


@app.route('/login', methods=['POST'])
def login_user():
    data = request.get_json() or request.form
    user = User.get_user_by_name(data.get('username'))
    if user and check_password_hash(user.password, data.get('password')):
        token = user.get_token()
        ValidLogin.log(user_id=user.id)
        return jsonify({'token': token})
    InvalidLogin.log(name=data.get('username'),
                     user_id=getattr(user, 'id', None),
                     password=data.get('password'))
    return make_response('Authorization Failed',  401)


if __name__ == "__main__":
    app.run()
