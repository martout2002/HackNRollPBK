import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_config.json") 
firebase_admin.initialize_app(cred)

# Access Firestore
db = firestore.client()
