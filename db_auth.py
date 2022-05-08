import firebase_admin
from firebase_admin import credentials, db

import os
print(os.getcwd())

# key_path = "resource/db_auth_key.json"
# db_url = "https://test-db-b261c-default-rtdb.firebaseio.com/"
# cred = credentials.Certificate(key_path)
# firebase_admin.initialize_app(cred, {'databaseURL' : db_url})
# dir = db.reference()