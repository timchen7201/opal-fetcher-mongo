from pydantic import BaseModel
from typing import Dict, Any, List

from motor.motor_asyncio import AsyncIOMotorClient
from opal_common.fetcher.events import FetchEvent
from opal_common.fetcher.fetch_provider import BaseFetchProvider
from opal_common.logger import get_logger

logger = get_logger("mongo_fetch_provider")

class MongoFetcherConfig(BaseModel):
    # Add any specific configuration properties needed for MongoDB fetching
   db_setting: Dict[str, str] = {
        'auth_db': str,
        'username': str,
        'password': str,
        'replica_set_name': str,
        'db': str,
        'table': str
    }
   query: Dict[str, Any] = {}
   fields: List[str] = []


class MongoFetchEvent(FetchEvent):
    fetcher: str = "MongoFetchProvider"
    config: MongoFetcherConfig = None
    

class MongoFetchProvider(BaseFetchProvider):
    def __init__(self, event: MongoFetchEvent) -> None:
        self._event: MongoFetchEvent
        super().__init__(event)
        self._mongo_client = None

    def parse_event(self, event: FetchEvent) -> MongoFetchEvent:
        return MongoFetchEvent(**event.dict(exclude={"config"}), config=event.config)

    async def __aenter__(self):
        # Initialize MongoDB client (replace with your connection details)
        self.db_setting = self._event.config.db_setting

        mongo_uri = (
            f'mongodb://{self.db_setting["username"]}:{self.db_setting["password"]}@{self._url}/{self.db_setting["db"]}'
            f'?authSource={self.db_setting["auth_db"]}&authMechanism=SCRAM-SHA-1'
        )
        try:
            self.pymongo_client = AsyncIOMotorClient(mongo_uri)
        except Exception as e:
            logger.error('connection failed: %s' % str(e))
        return self

    async def __aexit__(self, exc_type=None, exc_val=None, tb=None):
        # Close MongoDB client connection
        self.pymongo_client.close()

    async def _fetch_(self):
        # Fetch data from MongoDB (replace with your query logic)
        db = self.db_setting['db']
        table = self.db_setting['table']
        query = self._event.config.query
        fields = self._event.config.fields

        collection = self.pymongo_client[db][table]
        cursor = collection.find(query, {field: True for field in fields})
        result = await cursor.to_list(length=None)
        return result

    async def _process_(self, res):
        # Process the result if needed
        return res
