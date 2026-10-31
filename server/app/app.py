from flask import request, session
from flask_restful import Resource
from config import app, db, api
from models import User
from server.schemas.user_schema import UserSchema

class ClearSession(Resource):
    def delete(self):
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class Signup(Resource):
    def post(self):
        request_json = request.get_json()

        username = request_json.get('username')

        password = request_json.get('password')

        user = User(username = username)

        user.hash.password_hash = password

        try:
            
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return UserSchema().dump(user), 201
        
        except IntegrityError:
            return {'error': '422 unprocessable Entity'}, 422


class CheckSession(Resource):
    def get(self):
        if session.get('user_id'):
            user = User.query.filter(User.id == session['user_id']).first()
            return UserSchema().dump(user), 200
        return {}, 401

class Login(Resource):
    def post(self):

        username = request.get_json()['username']
        password = request.get_json()['password']

        user = User.query.filter(User.username == username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):

        if session.get('user_id'):
            session['user_id'] = None
            return {}, 204
        return {}, 401


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')

if __name__ == '__main__':
    app.run(port=5555, debug=True)    