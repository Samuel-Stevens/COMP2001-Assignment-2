from flask import Flask, request, jsonify
from flask_restx import Api, Resource, fields
from functools import wraps
import requests
import jwt
import datetime
from COMP_2001_Trail_Service import app, views
from authentication import token_required, role_required, SECRET_KEY

api = Api(
    app,
    version='1.0'
    
    
    )