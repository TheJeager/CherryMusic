from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from config import MONGO_DB_URI, DB_NAME
from ..logging import LOGGER

log = LOGGER(__name__)

mongo_client = AsyncIOMotorClient(
    MONGO_DB_URI,
    serverSelectionTimeoutMS=5000
)

mongodb = mongo_client[DB_NAME]


async def init_db():
    log.info("♻️ Connecting to your Mongo Database...")

    try:
        await mongo_client.admin.command("ping")
        log.info("🗃️ Connected to your Mongo Database.")

    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        log.error(f"❌ MongoDB Connection Failed: {e}")
        raise SystemExit(1)

    except Exception as e:
        log.error(f"❌ Unexpected MongoDB Error: {e}")
        raise SystemExit(1)