import logging
from typing import List, Union

from pymongo.mongo_client import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from sateda.data.measurements import MeasurementArray

logger = logging.getLogger(__name__)


class MongoDB:
    """
    Main class to connect to Mongo
    """

    def __init__(self, url: Union[str, None] = None, data_base: str = "", port: int = 27017) -> None:
        self.mongo_url: str | None = url
        self.mongo_db: str = data_base
        self.mongo_port: int = port
        self.mongo_client: MongoClient | None = None
        self.mongo_content: dict = {}
        self.list_collections: list = []

    def __enter__(self):
        self.connect()
        self.get_content()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.mongo_client.close()

    def connect(self) -> None:
        try:
            self.mongo_client = MongoClient(host=self.mongo_url, port=self.mongo_port)
            logger.debug(self.mongo_client.list_database_names())
        except ServerSelectionTimeoutError as err:
            raise ServerSelectionTimeoutError("Failed to connect to MongoDB server Timeout") from err
        except ConnectionError as err:
            raise ConnectionError("Failed to connect to MongoDB server") from err

        # print(self.mongo_client)

    def get_content(self) -> None:
        # logger.info(f"Getting content {self.mongo_url} {self.mongo_port} {self.mongo_db} ")
        for cursor in self.mongo_client[self.mongo_db]["Content"].find():
            self.mongo_content[cursor["type"]] = cursor["Values"]
            # print(cursor["type"])
        # print(self.mongo_content)
        self.mongo_content['Geometry'] = []
        geom  = self.mongo_client[self.mongo_db]["Geometry"].find_one({})
        if geom is None:
            logger.debug("Geometry not available")
        else:
            for i in geom:
                self.mongo_content['Geometry'].append(i)
            self.mongo_content['merged_measurement'] = self.mongo_content['Geometry'] + self.mongo_content['Measurements']
        self.mongo_content['states_fields'] = ['x', 'dx', 'P']

    def get_list_db(self) -> List[str]:
        return self.mongo_client.list_database_names()

    def get_list_collections(self) -> None:
        self.list_collections = []
        if self.mongo_client:
            self.list_collections = list(self.mongo_client[self.mongo_db].list_collection_names())

    def get_data(self, collection: str, state: str, site: List[str], sat: List[str], series:List[str], keys) -> list:
        """
        get_data getting data from mongo databases. 

        :param str collection: Collection to pull data from 
        :param str state: State to plot (if collection is state)
        :param List[str] site: List of site in the request
        :param List[str] sat: List of sat in the request
        :param List[str] series: List of series in the request
        :param List[str] keys: List of keys to pull from the database
        :raises ValueError: if no data is found
        :return list: of the data
        """
        logger.debug("getting data")
        agg_pipeline = [{"$match": {"Sat": {"$in": sat}, "Site": {"$in": site}, "Series": {"$in": series}}}]
        if state is not None:
            agg_pipeline[-1]["$match"]["State"] = {"$in": state}
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
        logger.info(agg_pipeline)
        cursor = self.mongo_client[self.mongo_db][collection].aggregate(agg_pipeline)
        #check if cursor is empty
        if not next(cursor, None):
            raise ValueError("No data found")
        return list(cursor)
    
    
    def get_data_to_measurement(self, collection: str, state: str, site: List[str], sat: List[str], series:List[str], keys) -> MeasurementArray:
        """
        get_data_to_measurement _summary_

        :param str collection: _description_
        :param str state: _description_
        :param List[str] site: _description_
        :param List[str] sat: _description_
        :param List[str] series: _description_
        :param _type_ keys: _description_
        :return MeasurementArray: Object measurement with the data
        """
        data = self.get_data(collection, state, site, sat, series, keys)
        array = MeasurementArray.from_mongolist(data)
        array.sort()
        return array
    
    
    def get_config(self) -> dict:
        return self.mongo_client[self.mongo_db]["Config"].find_one()
