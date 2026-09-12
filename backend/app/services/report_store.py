"""
MongoDB report storage service for Member 6.

Persists generated analysis reports into MongoDB (ip_sakti_db.reports)
and retrieves them by session_id UUID.
"""

import os
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
import pymongo

try:
    from dotenv import load_dotenv
    _ENV_PATH = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(dotenv_path=_ENV_PATH)
except ImportError:
    pass

logger = logging.getLogger(__name__)

_client: Optional[pymongo.MongoClient] = None
_db = None
_collection = None
_index_created = False


def _get_collection():
    global _client, _db, _collection, _index_created
    if _collection is not None:
        return _collection

    uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.environ.get("MONGODB_DB_NAME", "ip_sakti_db")

    try:
        _client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=3000)
        # Verify connection to server
        _client.admin.command("ping")
        _db = _client[db_name]
        _collection = _db["reports"]

        if not _index_created:
            _collection.create_index("session_id", unique=True)
            _index_created = True

        return _collection
    except Exception as exc:
        logger.error("Failed to connect to MongoDB")
        raise RuntimeError(
            "Database connection error: Unable to connect to MongoDB. "
            "Ensure MongoDB is running and MONGODB_URI is configured."
        ) from exc


def save(report: dict) -> str:
    """
    Saves a report dictionary to MongoDB.
    Generates a UUID session_id, attaches it to the report, inserts the document,
    and returns the session_id string.
    """
    collection = _get_collection()

    session_id = str(uuid.uuid4())
    report["session_id"] = session_id

    document = {
        "session_id": session_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report": report,
    }

    try:
        collection.insert_one(document)
    except Exception as exc:
        logger.error(f"Failed to save report {session_id} to MongoDB: {exc}")
        raise RuntimeError(f"Database write failed for session_id '{session_id}': {exc}") from exc

    return session_id


def get(session_id: str) -> Optional[dict]:
    """
    Retrieves a report dictionary from MongoDB by session_id.
    Returns None if session_id is not found.
    """
    collection = _get_collection()

    try:
        doc = collection.find_one({"session_id": session_id}, {"_id": 0})
    except Exception as exc:
        logger.error(f"Failed to query report {session_id} from MongoDB: {exc}")
        raise RuntimeError(f"Database query failed for session_id '{session_id}': {exc}") from exc

    if not doc:
        return None

    if "report" in doc and isinstance(doc["report"], dict):
        report_data = doc["report"]
        report_data["session_id"] = session_id
        return report_data

    return doc


def ping_db() -> bool:
    """
    Checks if MongoDB is reachable.
    Returns True if ping succeeds, False otherwise.
    """
    try:
        _get_collection()
        if _client is not None:
            _client.admin.command("ping")
            return True
        return False
    except Exception:
        logger.warning("Health check failed: unable to ping MongoDB")
        return False


