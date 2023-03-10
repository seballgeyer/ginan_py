import logging

from pymongo.mongo_client import MongoClient

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Main class to connect to Mongo
    """

    def __init__(self, url: str | None = None, data_base: str = "") -> None:
        self.mongo_url: str | None = url
        self.mongo_db: str = data_base
        self.mongo_client: MongoClient | None = None
        self.mongo_content: dict = {}
        self.list_collections: list = []

        if self.mongo_url:
            self.connect()
            self.get_content()

    def connect(self) -> None:
        self.mongo_client = MongoClient(host=self.mongo_url)
        print(self.mongo_client)

    def get_content(self) -> None:
        print(self.mongo_client)
        for cursor in self.mongo_client[self.mongo_db]["Content"].find():
            self.mongo_content[cursor["type"]] = cursor["Values"]

    def get_list_db(self) -> None:
        self.list_collections = []
        if self.mongo_client:
            self.list_collections = list(self.mongo_client[self.mongo_db].list_collection_names())

    def get_data(self, collection, state, site, sat, series, keys) -> list:
        """
        hardcoded... yet.
        """
        logger.debug("getting data")
        agg_pipeline = [{"$match": {"Sat": {"$in": sat}, "Site": {"$in": site}, "Series": {"$in": [series]}}}]
        if state is not None:
            agg_pipeline[-1]["$match"]["State"] = state
        agg_pipeline.append({"$sort": {"Epoch": 1}})
        agg_pipeline.append(
            {
                "$group": {
                    "_id": {"site": "$Site", "sat": "$Sat", "series": "$Series"},
                    "t": {"$push": "$Epoch"},
                }
            }
        )
        for key in keys:
            agg_pipeline[-1]["$group"][key] = {"$push": f"${key}"}
        cursor = self.mongo_client[self.mongo_db][collection].aggregate(agg_pipeline)
        return list(cursor)
