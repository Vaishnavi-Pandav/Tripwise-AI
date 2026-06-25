"""
Firebase Admin SDK initialisation.
Called once at app startup to enable server-side Firebase token verification.
"""
import logging
import firebase_admin
from firebase_admin import credentials

logger = logging.getLogger("tripwise")

_initialized = False


def init_firebase():
    """
    Initialise Firebase Admin SDK using the project ID from env.
    No service account key is required for token verification —
    Firebase Admin can verify tokens using just the project ID.
    """
    global _initialized
    if _initialized:
        return
    try:
        # If no credentials file is provided, Firebase Admin uses Application
        # Default Credentials — for local dev this works without a key file.
        # We pass the project_id explicitly so it doesn't need ADC.
        from app.core.config import settings
        project_id = getattr(settings, "FIREBASE_PROJECT_ID", "")
        if project_id:
            app = firebase_admin.initialize_app(
                credential=credentials.ApplicationDefault(),
                options={"projectId": project_id},
            )
        else:
            # No project ID — initialise without options (uses env GOOGLE_APPLICATION_CREDENTIALS)
            firebase_admin.initialize_app()
        _initialized = True
        logger.info("Firebase Admin SDK initialised")
    except Exception as e:
        logger.warning(f"Firebase Admin SDK not initialised: {e}. Token verification disabled.")
