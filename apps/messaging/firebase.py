import os
import json
import firebase_admin
from firebase_admin import credentials

default_app = None

def init_firebase():
    global default_app
    if not firebase_admin._apps:
        firebase_creds = os.getenv("FIREBASE_CREDENTIALS")
        if not firebase_creds:
            raise RuntimeError("FIREBASE_CREDENTIALS not found in environment")

        try:
            cred = credentials.Certificate(json.loads(firebase_creds))
            default_app = firebase_admin.initialize_app(cred)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Firebase: {e}")

    return default_app
