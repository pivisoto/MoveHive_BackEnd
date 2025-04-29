from functools import wraps
from flask import request, jsonify
import jwt

SECRET_KEY = 'move'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]

        if not token:
            return jsonify({'erro': 'Token é obrigatório!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'erro': 'Token expirado!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'erro': 'Token inválido!'}), 401

        return f(*args, **kwargs)
    
    return decorated
