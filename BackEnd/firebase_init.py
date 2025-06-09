import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, initialize_app, get_app

load_dotenv()

def initialize_firebase():
    try:
        return get_app()
    except ValueError:
        cred_path = os.getenv("FIREBASE")
        cred = credentials.Certificate(cred_path)
        return initialize_app(cred, {
            'storageBucket': 'safeviewbd.appspot.com'
        })