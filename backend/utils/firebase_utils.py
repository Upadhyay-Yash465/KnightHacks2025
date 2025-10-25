"""
Firebase utilities for storing transcripts and analysis results.
Handles Firestore and Firebase Storage operations.
"""

import os
from typing import Dict, Any
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, storage


# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK with credentials."""
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_KEY_PATH", "firebase-key.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET", "your-project.appspot.com")
            })
        else:
            # Use default credentials (for testing)
            firebase_admin.initialize_app()


initialize_firebase()


def save_to_firestore(transcript: str, feedback: Dict[str, Any], user_id: str = "default") -> str:
    """
    Save transcript and feedback to Firestore.
    
    Args:
        transcript: The transcribed text
        feedback: Analysis results containing filler_count, clarity_score, suggestions, summary
        user_id: User identifier
        
    Returns:
        Document ID of the saved record
    """
    db = firestore.client()
    
    doc_data = {
        "transcript": transcript,
        "filler_count": feedback.get("filler_count", 0),
        "clarity_score": feedback.get("clarity_score", 0.0),
        "suggestions": feedback.get("suggestions", []),
        "summary": feedback.get("summary", ""),
        "timestamp": datetime.utcnow(),
        "user_id": user_id
    }
    
    doc_ref = db.collection("speech_analysis").add(doc_data)
    return doc_ref[1].id


def upload_to_storage(file_path: str, file_name: str) -> str:
    """
    Upload file to Firebase Storage.
    
    Args:
        file_path: Local path to the file
        file_name: Name to use in Firebase Storage
        
    Returns:
        Public URL of the uploaded file
    """
    bucket = storage.bucket()
    blob = bucket.blob(f"audio/{file_name}")
    
    blob.upload_from_filename(file_path)
    blob.make_public()
    
    return blob.public_url


def get_analysis_history(user_id: str = "default", limit: int = 10) -> list:
    """
    Retrieve analysis history for a user.
    
    Args:
        user_id: User identifier
        limit: Maximum number of records to retrieve
        
    Returns:
        List of analysis records
    """
    db = firestore.client()
    
    docs = db.collection("speech_analysis") \
        .where("user_id", "==", user_id) \
        .order_by("timestamp", direction=firestore.Query.DESCENDING) \
        .limit(limit) \
        .stream()
    
    return [{**doc.to_dict(), "id": doc.id} for doc in docs]

