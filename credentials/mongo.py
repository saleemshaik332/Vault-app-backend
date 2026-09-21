"""
MongoDB connection for the password/credential vault.

Kept separate from the SQL database on purpose: credential entries are
free-form (service name, username, password, notes, URL) and this app
demonstrates the polyglot-persistence setup requested (SQL for structured
records, MongoDB for the flexible credential vault).

The connection is lazy — it only connects when a request actually needs it,
so the rest of the site keeps working even if MongoDB isn't running.
"""
from django.conf import settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError

_client = None


class MongoUnavailable(Exception):
    pass


def get_collection():
    global _client
    try:
        if _client is None:
            _client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
            _client.admin.command('ping')  # fail fast if unreachable
        db = _client[settings.MONGO_DB_NAME]
        return db['credentials']
    except PyMongoError as exc:
        _client = None
        raise MongoUnavailable(
            "Could not connect to MongoDB. Make sure it's running and MONGO_URI is set correctly."
        ) from exc
