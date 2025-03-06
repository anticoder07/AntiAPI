from flask import g, request
from functools import wraps
from flask_jwt_extended import decode_token
from src.repositories.token_repository import get_token_by_value
from datetime import datetime
import jwt

def bearer_token_required(f):
   @wraps(f)
   def decorated_function(*args, **kwargs):
       auth_header = request.headers.get('Authorization')
       if not auth_header or not auth_header.startswith('Bearer '):
           return {"error": "Missing or invalid Authorization header"}, 401

       token = auth_header.split("Bearer ")[1]

       try:
           decoded_token = decode_token(token)
           company_id = decoded_token['sub']

           db_token = get_token_by_value(token)
           if not db_token or db_token.expires_at < datetime.utcnow():
               return {"error": "Invalid or expired token"}, 401

           # Lưu company_id vào g
           g.company_id = company_id
           return f(*args, **kwargs)

       except jwt.ExpiredSignatureError:
           return {"error": "Token has expired"}, 401
       except jwt.InvalidTokenError:
           return {"error": "Invalid token"}, 401

   return decorated_function

def project_token_required(f):
   @wraps(f)
   def decorated_function(*args, **kwargs):
       project_token = request.headers.get('X-Project-Token')
       if not project_token:
           return {"error": "Missing Project Token"}, 401

       try:
           db_project_token = get_token_by_value(project_token)
           if not db_project_token or db_project_token.expires_at < datetime.utcnow():
               return {"error": "Invalid or expired Project token"}, 401

           # Lưu project_token vào g
           g.project_token = project_token
           return f(*args, **kwargs)

       except Exception as e:
           return {"error": "Project token validation failed"}, 401

   return decorated_function