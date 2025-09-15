import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    # Get the path to service account key from environment
    service_account_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if not service_account_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
    
    # Initialize Firebase Admin with service account
    cred = credentials.Certificate(service_account_path)
    firebase_admin.initialize_app(cred, {
        'projectId': os.getenv("FIREBASE_PROJECT_ID", "student-wellness-backend")
    })

# Create Firestore client
db = firestore.Client()

# Helper function to get database instance
def get_db():
    return db
