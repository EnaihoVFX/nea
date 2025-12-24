import firebase_admin
from firebase_admin import auth, credentials
from fastapi import Header, HTTPException, status
import os

def init_firebase(key_path: str):
    """Initializes Firebase Admin SDK."""
    if not os.path.exists(key_path):
        print(f"Warning: {key_path} not found. Authentication will only work with mock tokens.")
        return

    try:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully.")
    except Exception as e:
        print(f"Error initializing Firebase: {e}")

def require_user(authorization: str = Header(None)) -> str:
    """
    Dependency to verify the Firebase ID token in the Authorization header.
    Supports a mock token 'test-token' for testing purposes.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected 'Bearer <token>'",
        )
    
    token = authorization.split("Bearer ")[1]
    
    # Mock token for testing
    if token == "test-token":
        return "testuser_uid"
        
    try:
        # Check if firebase is initialized
        if not firebase_admin._apps:
             raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Firebase is not initialized and no mock token was provided.",
            )
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )
