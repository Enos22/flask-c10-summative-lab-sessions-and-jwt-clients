from flask import request, session
from flask_restful import Resource

from extensions import db
from models.user import User
from schemas.user_schema import user_schema


class Signup(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")
        confirmation = data.get("password_confirmation")

        if not username:
            return {"errors": ["Username is required"]}, 422
        if not password:
            return {"errors": ["Password is required"]}, 422
        if password != confirmation:
            return {"errors": ["Passwords do not match"]}, 422
        if User.query.filter_by(username=username).first():
            return {"errors": ["Username already exists"]}, 422

        try:
            user = User(username=username)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
            session.clear()
            session["user_id"] = user.id
            return user_schema.dump(user), 201
        except (ValueError, Exception) as exc:
            db.session.rollback()
            return {"errors": [str(exc)]}, 422


class Login(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        user = User.query.filter_by(username=data.get("username")).first()
        password = data.get("password")
        if user and password and user.authenticate(password):
            session.clear()
            session["user_id"] = user.id
            return user_schema.dump(user), 200
        return {"errors": ["Invalid username or password"]}, 401


class Logout(Resource):
    def delete(self):
        session.clear()
        return {}, 204


class CheckSession(Resource):
    def get(self):
        user = db.session.get(User, session.get("user_id"))
        if user is None:
            return {"errors": ["Authentication required"]}, 401
        return user_schema.dump(user), 200


class ClearSession(Resource):
    def delete(self):
        session.clear()
        return {}, 204
