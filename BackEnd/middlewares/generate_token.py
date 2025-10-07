import jwt
import datetime

SECRET_KEY = 'move'

def generate_token(user_id, tipo_usuario="usuario"):

    payload = {
        'user_id': user_id,
        'tipo_usuario':tipo_usuario,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=365) 
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
