from functools import wraps
from flask import request, jsonify, session
import jwt
import datetime

SECRET_KEY = "COMP2001Trails"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'email' not in session:
            return {'message': 'User not logged in'}, 401
        request.user_data = {'email': session['email'], 'role': session['role']}
        return f(*args, **kwargs)
    return decorated

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if request.user_data.get('role') != role:
                return {'message': 'Unauthorized, insufficient role'}, 403
            return f(*args, **kwargs)
        return decorated
    return wrapper

def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_data = getattr(request, 'user_data', None)
            if not user_data or user_data.get('role') != role:
                return {'message': 'Unauthorized, insufficient role'}, 403
            return f(*args, **kwargs)
        return decorated
    return wrapper