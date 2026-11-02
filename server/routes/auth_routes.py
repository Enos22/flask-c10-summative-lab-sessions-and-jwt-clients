from flask import request, session
from flask_restful import Resource
from app.config import app, db, api
from models.user import User
from schemas.user_schema import UserSchema

PUBLIC_ENDPOINTS = {'signup', 'login', 'check_session'}

@app.before_request
def check_if_logged_in():
    if request.endpoint not in PUBLIC_ENDPOINTS and not session.get('user_id'):
        return {'errors': ['Authentication required.']}, 401

class ClearSession(Resource):
    def delete(self):
        session.clear()
        return {}, 204

class Signup(Resource):
    def post(self):
        request_json = request.get_json(silent=True) or {}
        username = request_json.get('username')
        password = request_json.get('password')
        password_confirmation = request_json.get('password_confirmation')

        if not isinstance(username, str) or not username.strip():
            return {'errors': ['A username is required.']}, 422
        if not isinstance(password, str) or not password:
            return {'errors': ['A password is required.']}, 422
        if password != password_confirmation:
            return {'errors': ['Passwords do not match.']}, 422
        username = username.strip()
        if User.query.filter_by(username=username).first():
            return {'errors': ['That username is already taken.']}, 422
        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
            session.clear()
            session['user_id'] = user.id
            return UserSchema().dump(user), 201
        except ValueError as e:
            db.session.rollback()
            return {'errors': [str(e)]}, 422

class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = db.session.get(User, session['user_id'])
            if user is None:
                session.clear()
                return {'errors': ['Authentication required.']}, 401
            return UserSchema().dump(user), 200
        return {'errors': ['Authentication required.']}, 401

class Login(Resource):
    def post(self):
        request_json = request.get_json(silent=True) or {}
        username = request_json.get('username')
        password = request_json.get('password')
        if not isinstance(username, str) or not isinstance(password, str):
            return {'errors': ['Username and password are required.']}, 422

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session.clear()
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        return {'errors': ['Invalid username or password.']}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.clear()
            return {}, 204
        return {'errors': ['Authentication required.']}, 401


api.add_resource(ClearSession, '/clear', endpoint='clear')
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)