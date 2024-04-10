#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe


@app.before_request
def check_if_logged_in():
    end_point = ["signup", "login", "check_session"]
    if request.endpoint not in end_point and not session.get("user_id"):
        return {"error": "401: Unauthorized"}, 401


class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            user = User()
            for attr, value in data.items():
                if hasattr(user, attr):
                    setattr(user, attr, value)
            user.password = data.get("password")
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            return user.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 422


class CheckSession(Resource):
    def get(self):
        try:
            if user_id := session.get("user_id"):
                user = db.session.get(User, user_id)
                return user.to_dict(), 200
            return {}, 401
        except Exception as e:
            return {"message": str(e)}, 422


class Login(Resource):
    def post(self):
        try:
            data = request.json
            user = User.query.filter_by(username=data.get("username")).first()
            if user and user.authenticate(data.get("password")):
                session["user_id"] = user.id
                return user.to_dict(), 200
            else:
                return {"error": "Invalid Credentials"}, 401
        except Exception as e:
            return {"error": str(e)}, 422


class Logout(Resource):
    def delete(self):
        session["user_id"] = None
        return {}, 204


class RecipeIndex(Resource):
    def get(self):
        if user := User.query.filter(User.id == session["user_id"]).first():
            return [recipe.to_dict() for recipe in user.recipes], 200
        else:
            return {"error": "unable to process request"}, 401

    def post(self):
        try:
            data = request.get_json()
            new_recipe = Recipe(**data)
            new_recipe.user_id = session.get("user_id")
            db.session.add(new_recipe)
            db.session.commit()
            return new_recipe.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 422


api.add_resource(Signup, "/signup", endpoint="signup")
api.add_resource(CheckSession, "/check_session", endpoint="check_session")
api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Logout, "/logout", endpoint="logout")
api.add_resource(RecipeIndex, "/recipes", endpoint="recipes")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
