import time
import firebase_admin
from firebase_admin import credentials, db

key_path = "test-db-b261c-firebase-adminsdk-ddkpv-ff4ed08001.json"
db_url = "https://test-db-b261c-default-rtdb.firebaseio.com/"
cred = credentials.Certificate(key_path)
firebase_admin.initialize_app(cred, {'databaseURL' : db_url})
dir = db.reference()

while True:
    ref = db.reference()
    
    db_dict = ref.get()

    for i, each in enumerate(db_dict):
        # if (len(db_dict) - i) <= 3:
        print(i, each, db_dict[each])
    

    print("-"*20)        

    time.sleep(3)
    