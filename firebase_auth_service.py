"""
Firebase Authentication Integration for FastAPI
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt.exceptions import InvalidTokenError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        if not firebase_admin._apps:
            # Try to get credentials from environment variable
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
            else:
                # Use default credentials (for Google Cloud environments)
                cred = credentials.ApplicationDefault()
            
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        else:
            logger.info("Firebase Admin SDK already initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {str(e)}")
        raise

# Initialize Firebase
initialize_firebase()

# Get Firestore client
db = firestore.client()

# Security scheme
security = HTTPBearer()

class FirebaseAuth:
    """Firebase Authentication helper class"""
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token and return decoded token data
        
        Args:
            token: Firebase ID token
            
        Returns:
            Decoded token data
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            # Verify the token with Firebase
            decoded_token = firebase_auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """
        Get current authenticated user from Firebase token
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            User data from Firebase
        """
        token = credentials.credentials
        decoded_token = FirebaseAuth.verify_token(token)
        
        # Get user data from Firebase Auth
        try:
            user_record = firebase_auth.get_user(decoded_token['uid'])
            return {
                'uid': user_record.uid,
                'email': user_record.email,
                'display_name': user_record.display_name,
                'email_verified': user_record.email_verified,
                'photo_url': user_record.photo_url,
                'disabled': user_record.disabled,
                'metadata': {
                    'creation_timestamp': user_record.user_metadata.get('creation_timestamp'),
                    'last_sign_in_timestamp': user_record.user_metadata.get('last_sign_in_timestamp'),
                }
            }
        except Exception as e:
            logger.error(f"Failed to get user data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to retrieve user data",
            )
    
    @staticmethod
    async def get_user_from_firestore(uid: str) -> Optional[Dict[str, Any]]:
        """
        Get user data from Firestore
        
        Args:
            uid: User ID
            
        Returns:
            User data from Firestore or None
        """
        try:
            doc_ref = db.collection('users').document(uid)
            doc = doc_ref.get()
            
            if doc.exists:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                return user_data
            return None
        except Exception as e:
            logger.error(f"Failed to get user from Firestore: {str(e)}")
            return None
    
    @staticmethod
    async def create_user_in_firestore(uid: str, user_data: Dict[str, Any]) -> bool:
        """
        Create user document in Firestore
        
        Args:
            uid: User ID
            user_data: User data to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = db.collection('users').document(uid)
            doc_ref.set({
                **user_data,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
            logger.info(f"User document created in Firestore for UID: {uid}")
            return True
        except Exception as e:
            logger.error(f"Failed to create user in Firestore: {str(e)}")
            return False
    
    @staticmethod
    async def update_user_in_firestore(uid: str, update_data: Dict[str, Any]) -> bool:
        """
        Update user document in Firestore
        
        Args:
            uid: User ID
            update_data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            doc_ref = db.collection('users').document(uid)
            doc_ref.update({
                **update_data,
                'updated_at': datetime.utcnow(),
            })
            logger.info(f"User document updated in Firestore for UID: {uid}")
            return True
        except Exception as e:
            logger.error(f"Failed to update user in Firestore: {str(e)}")
            return False
    
    @staticmethod
    async def save_session_to_firestore(uid: str, session_data: Dict[str, Any]) -> bool:
        """
        Save speech analysis session to Firestore
        
        Args:
            uid: User ID
            session_data: Session data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            sessions_ref = db.collection('users').document(uid).collection('sessions')
            sessions_ref.add({
                **session_data,
                'created_at': datetime.utcnow(),
            })
            logger.info(f"Session saved to Firestore for UID: {uid}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session to Firestore: {str(e)}")
            return False
    
    @staticmethod
    async def get_user_sessions(uid: str, limit: int = 50) -> list:
        """
        Get user's speech analysis sessions from Firestore
        
        Args:
            uid: User ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of sessions
        """
        try:
            sessions_ref = db.collection('users').document(uid).collection('sessions')
            sessions = sessions_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit).stream()
            
            session_list = []
            for session in sessions:
                session_data = session.to_dict()
                session_data['id'] = session.id
                session_list.append(session_data)
            
            return session_list
        except Exception as e:
            logger.error(f"Failed to get user sessions: {str(e)}")
            return []
    
    @staticmethod
    async def get_user_stats(uid: str) -> Dict[str, Any]:
        """
        Get user's speech analysis statistics
        
        Args:
            uid: User ID
            
        Returns:
            User statistics
        """
        try:
            sessions = await FirebaseAuth.get_user_sessions(uid, limit=1000)
            
            if not sessions:
                return {
                    'total_sessions': 0,
                    'average_clarity_score': 0,
                    'total_filler_words': 0,
                    'improvement_trend': 0,
                }
            
            total_sessions = len(sessions)
            clarity_scores = [s.get('analysis', {}).get('clarity_score', 0) for s in sessions if s.get('analysis')]
            filler_counts = [s.get('analysis', {}).get('filler_count', 0) for s in sessions if s.get('analysis')]
            
            average_clarity_score = sum(clarity_scores) / len(clarity_scores) if clarity_scores else 0
            total_filler_words = sum(filler_counts)
            
            # Calculate improvement trend (comparing first half vs second half)
            if len(clarity_scores) >= 4:
                mid_point = len(clarity_scores) // 2
                first_half_avg = sum(clarity_scores[:mid_point]) / mid_point
                second_half_avg = sum(clarity_scores[mid_point:]) / (len(clarity_scores) - mid_point)
                improvement_trend = second_half_avg - first_half_avg
            else:
                improvement_trend = 0
            
            return {
                'total_sessions': total_sessions,
                'average_clarity_score': round(average_clarity_score, 2),
                'total_filler_words': total_filler_words,
                'improvement_trend': round(improvement_trend, 2),
            }
        except Exception as e:
            logger.error(f"Failed to get user stats: {str(e)}")
            return {
                'total_sessions': 0,
                'average_clarity_score': 0,
                'total_filler_words': 0,
                'improvement_trend': 0,
            }

# Dependency for getting current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """FastAPI dependency to get current authenticated user"""
    return await FirebaseAuth.get_current_user(credentials)

# Optional authentication dependency
async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """FastAPI dependency to get current user (optional)"""
    if not credentials:
        return None
    try:
        return await FirebaseAuth.get_current_user(credentials)
    except HTTPException:
        return None

