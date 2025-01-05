from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from functools import wraps
import requests
import jwt
import datetime
import procedures
from __init__ import app
from authentication import token_required, role_required, SECRET_KEY

CORS(app)

api = Api(
    app,
    version='1.0',
    title='COMP2001 Trail Microservice by Samuel Stevens',
    description='API enableing the trail application to function by providing the ability to manage users, trails, and features',
    doc='/swagger',
    security='BearerAuth'
)

api.authorizations = {
    'BearerAuth': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
    }
}


health_ns = api.namespace('Health', description='Health Check for Server')

@health_ns.route('/ping')
class Ping(Resource):
    @api.doc(description="Ping the server to check its status")
    @api.response(200, "Success", example={"message": "pong"})
    def get(self):
        """Returns a pong response to confirm the server is running"""
        return {"message": "pong"}, 200

users_ns = api.namespace('Users', description='User operations')
trails_ns = api.namespace('Trails', description='Trail operations')
feature_ns = api.namespace('Features', desciption='Feature operations')

user_model = api.model('User', {
    'UserID': fields.Integer(required=True, description='The user ID'),
    'Username': fields.String(required=True, description='The users name'),
    'Email': fields.String(required=True, description='The users email address'),
    'Password': fields.String(required=True, description='The users password'),
    'Role': fields.String(required=True, description='The role of the user'),
})


@users_ns.route('')
class Users(Resource):
    @users_ns.doc('get_all_users')
    def get(self):
        return procedures.fetch_all_users()





if __name__ == '__main__':
    from os import environ 
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '8000'))
    except ValueError:
        PORT = 8000
    app.run(HOST, PORT)



