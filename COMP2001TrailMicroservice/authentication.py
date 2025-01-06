from functools import wraps
from flask import request, jsonify
import jwt
import datetime

SECRET_KEY = "COMP2001Trails"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing'}, 401
        try:
            token = token.replace('Bearer ', '')
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"], options={"verify_exp": True})
            request.user_data = data
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Invalid token'}, 401
        return f(*args, **kwargs)
    return decorated

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

