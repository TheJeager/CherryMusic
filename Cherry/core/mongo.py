from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import MONGO_DB_URI, DB_NAME
from ..logging import LOGGER

LOGGER(__name__).info("♻️ Connecting to your Mongo Database...")

try:
    mongo_client = MongoClient(
        MONGO_DB_URI,
        serverSelectionTimeoutMS=5000
    )

    mongodb = mongo_client[DB_NAME]

    mongo_client.admin.command("ping")

    LOGGER(__name__).info("🗃️ Connected to your Mongo Database.")

except (ConnectionFailure, ServerSelectionTimeoutError) as e:
    LOGGER(__name__).error(f"❌ MongoDB Connection Failed: {e}")
    exit(1)
except Exception as e:
    LOGGER(__name__).error(f"❌ Unexpected MongoDB Error: {e}")
    exit(1)
