import jwt
import datetime

SECRET_KEY = 'move'

def generate_token(user_id):

    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24) 
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token
