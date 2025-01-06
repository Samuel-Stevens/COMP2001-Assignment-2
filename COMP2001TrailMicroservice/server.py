from flask import Flask, request, jsonify, session
from flask_restx import Api, Resource, fields
from flask_cors import CORS
from functools import wraps
from flask_session import Session
import requests
import jwt
from datetime import timedelta
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
feature_ns = api.namespace('Feature', description='Feature operations')
authentication_ns = api.namespace('Authentication', description='Authentication operations')

user_model = api.model('User', {
    'Username': fields.String(required=True, description='The users name'),
    'Email': fields.String(required=True, description='The users email address'),
    'Password': fields.String(required=True, description='The users password'),
    'Role': fields.String(required=True, description='The role of the user'),
})

trail_model = api.model('Trail', {
    'TrailName': fields.String(required=True, description='The name of the trail'),
    'TrailSummary': fields.String(required=True, description='A summary of the trail'),
    'TrailDescription': fields.String(required=True, description='A description of the trail'),
    'Difficulty': fields.String(required=True, description='The trails difficulty'),
    'Location': fields.String(required=True, description='The location of the trail'),
    'Length': fields.Float(required=True, description='The distance of the trail in kilometers'),
    'ElevationGain': fields.Float(required=True, description='The elevation gain of the trail in meters'),
    'RouteType': fields.String(required=True, description='The type of route'),
    'OwnerID': fields.Integer(required=True, description='The user ID of the trail owner'),
    'Pt1_Lat': fields.Float(required=True, description='Latitude of Point 1'),
    'Pt1_Long': fields.Float(required=True, description='Longitude of Point 1'),
    'Pt1_Desc': fields.String(required=True, description='Description of Point 1'),
    'Pt2_Lat': fields.Float(required=True, description='Latitude of Point 2'),
    'Pt2_Long': fields.Float(required=True, description='Longitude of Point 2'),
    'Pt2_Desc': fields.String(required=True, description='Description of Point 2'),
    'Pt3_Lat': fields.Float(required=True, description='Latitude of Point 3'),
    'Pt3_Long': fields.Float(required=True, description='Longitude of Point 3'),
    'Pt3_Desc': fields.String(required=True, description='Description of Point 3'),
    'Pt4_Lat': fields.Float(required=True, description='Latitude of Point 4'),
    'Pt4_Long': fields.Float(required=True, description='Longitude of Point 4'),
    'Pt4_Desc': fields.String(required=True, description='Description of Point 4'),
    'Pt5_Lat': fields.Float(required=True, description='Latitude of Point 5'),
    'Pt5_Long': fields.Float(required=True, description='Longitude of Point 5'),
    'Pt5_Desc': fields.String(required=True, description='Description of Point 5'),
})

feature_model = api.model('Feature', {
    'TrailFeature': fields.String(required=True, description='The name of the feature'),
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='The email of the user'),
    'password': fields.String(required=True, description='The password of the user'),
})

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = SECRET_KEY  
Session(app)

AUTH_API_URL = "https://web.socem.plymouth.ac.uk/COMP2001/auth/api/users"


@authentication_ns.route('/login')
class Login(Resource):
    @authentication_ns.doc('user_login')
    @authentication_ns.expect(login_model)
    def post(self):
        """Authenticate user with the Auth API and create a session for API access"""
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return {'message': 'Email and password are required'}, 400

        try:
            response = requests.post(
                AUTH_API_URL,
                json={"email": email, "password": password},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                try:
                    auth_response = response.json()
                    if isinstance(auth_response, list) and len(auth_response) >= 2 and auth_response[0] == "Verified":
                        verified_status = auth_response[1]

                        # Store the user data in session
                        session['email'] = email
                        session['role'] = 'Admin' if verified_status == "True" else 'User'

                        return {
                            "message": "Login successful",
                            "verified": verified_status == "True",
                            "role": session['role']
                        }, 200

                    else:
                        return {"message": "Unexpected API response format", "response_content": auth_response}, 500

                except ValueError:
                    return {"message": "Invalid JSON response from Auth API"}, 500

            else:
                return {
                    "message": f"Authentication failed with status code {response.status_code}",
                    "response_text": response.text
                }, response.status_code

        except requests.RequestException as e:
            return {"message": f"Error connecting to Auth API: {str(e)}"}, 500


@users_ns.route('')
class Users(Resource):
    @users_ns.doc('get_all_users')
    def get(self):
        """Get all users details"""
        return procedures.fetch_all_users()

    @users_ns.expect(user_model)
    @users_ns.doc('create_user')
    def post(self):
        """Create a new User"""
        return procedures.create_user()

@users_ns.route('/<string:user_id>')
@users_ns.param('user_id', 'The users ID')
class User(Resource):
    @users_ns.doc('get_user_by_id', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def get(self, user_id):
        """Fetch a specific User """
        return procedures.fetch_user_by_id(user_id)

    @users_ns.expect(user_model)
    @users_ns.doc('update_user', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def put(self, user_id):
        return procedures.update_user(user_id)

    @users_ns.doc('delete_user', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def delete(self, user_id):
        return procedures.delete_user(user_id)


@trails_ns.route('/')
class Trails(Resource):
    @trails_ns.doc('get_all_trails')
    def get(self):
        """Fetch all trails"""
        return procedures.fetch_all_trails()

    @trails_ns.expect(trail_model)
    @trails_ns.doc('create_trail', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def post(self):
        """Create a new trail"""
        return procedures.create_trail()

@trails_ns.route('/<string:TrailID>')
@trails_ns.param('TrailID', 'The Trail ID')
class Trail(Resource):
    @trails_ns.doc('delete_trail', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def delete(self, TrailID):
        """Delete a trail by its ID"""
        return procedures.delete_trail(TrailID)

    @trails_ns.expect(trail_model)
    @trails_ns.doc('update_trail', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def put(self, TrailID):
        """Update a trail using its ID"""
        return procedures.update_trail(TrailID)

    @trails_ns.doc('fetch_trail_by_id', security='BearerAuth')
    def get(self, TrailID):
        """Fetch a specific trail using its ID"""
        return procedures.fetch_trail_by_id(TrailID)


@feature_ns.route('/')
class Feature(Resource):

    @feature_ns.doc('get_all_features')
    def get(self):
        """Fetch all features"""
        return procedures.fetch_all_features()

    @feature_ns.expect(feature_model)
    @feature_ns.doc('create_feature', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def post(self):
        """Create a new feature"""
        return procedures.create_feature()

@feature_ns.route('/<string:feature_id>')
@feature_ns.param('feature_id', 'The feature ID')
class Feature(Resource):
    @feature_ns.doc('get_feature_by_id')
    def get(self, feature_id):
        return procedures.fetch_feature_by_id(feature_id)

    @feature_ns.expect(feature_model)
    @feature_ns.doc('update_feature', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def put(self, feature_id):
        return procedures.update_Feature(feature_id)

    @feature_ns.doc('delete_feature', security='BearerAuth')
    @token_required
    @role_required('Admin')
    def delete(self, feature_id):
        return procedures.delete_feature(feature_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)






