from datetime import datetime

from bson.objectid import ObjectId
from flask import session as flask_session
from pymongo import MongoClient, ReadPreference, WriteConcern
from pymongo.read_concern import ReadConcern

from instance import config


class MongoHandler:

    def __init__(self, with_session: bool = True):
        """
            Class to Perform Mongo Operations
            :param with_session
        """
        try:
            self.client = MongoClient(config.MONGO_ATLAS_CONNECTION_STRING)
        except Exception:
            raise Exception("Mongo Connection not implemented")

        if with_session:
            self.session = self.client.start_session(causal_consistency=True)
            self.session.start_transaction(read_concern=ReadConcern('majority'), write_concern=WriteConcern('majority'),
                                           read_preference=ReadPreference.PRIMARY)
        else:
            self.session = None

    def get_client(self):
        """
        Get the Mongodb client.
        :return:
        """
        return self.client

    def close_client(self):
        """
        Releases any valuable MongoDb Resources
        :return:
        """
        self.client.close()

    def get_pymongo_db(self, db_name: str):
        """
        Gets the Mongodb database specified by db_name
        :param db_name:
        :return:
        """
        if flask_session:
            return self.client['hospital_management']
        return self.client[db_name]

    def insert_doc(self, obj_json_to_insert: dict, db_name: str, collection_name: str,session=None):
        """
        Inserts the document
        :param obj_json_to_insert:
        :param db_name:
        :param collection_name:
        :param session:
        :return:
        """
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        obj_json_to_insert['last_modified_time'] = datetime.utcnow()
        return collection.insert_one(obj_json_to_insert, session=self.session)

    def insert_doc_many(self, obj_dict_list: list, db_name: str, collection_name: str, session=None):
        """
        Inserts list to documents
        :param obj_dict_list:
        :param db_name:
        :param collection_name:
        :param session:
        :return:
        """
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        return collection.insert_many(obj_dict_list, session=self.session)

    def update_doc(self, obj_json_to_query: dict, obj_json_to_update: dict, db_name: str, collection_name: str):
        """
        Updates multiple documents
        :param obj_json_to_query:
        :param obj_json_to_update:
        :param db_name:
        :param collection_name:
        :return:
        """
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        obj_json_to_update['last_modified_time'] = datetime.utcnow()
        return collection.update_many(obj_json_to_query, {'$set': obj_json_to_update}, session=self.session)

    def update_one_doc(self, obj_json_to_query: dict, obj_json_to_update: dict, db_name: str, collection_name: str,
                       unset_json: dict = None, is_by_pass_schema: bool = False, session=None):
        """
        Updates the document
        :param obj_json_to_query:
        :param obj_json_to_update:
        :param db_name:
        :param collection_name:
        :param unset_json:
        :param is_by_pass_schema:
        :param session:
        :return:
        """
        if unset_json is None:
            unset_json = {}
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        obj_json_to_update['last_modified_time'] = datetime.utcnow()
        if unset_json:
            return collection.update_one(obj_json_to_query, {'$set': obj_json_to_update, '$unset': unset_json},
                                         session=self.session)

        return collection.update_one(obj_json_to_query, {'$set': obj_json_to_update}, session=self.session)

    def filter_one_doc(self, db_name: str, collection_name: str, filter_json: dict, projection: dict = None,
                       sort_json=None, session=None):
        """
        Gets only the matching document from the specified collection by applying the filter passed in the filter_json.
        :param db_name:
        :param collection_name:
        :param filter_json:
        :param projection:
        :param sort_json:
        :param session:
        :return:
        """
        if sort_json is None:
            sort_json = {}
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        if sort_json:
            return collection.find_one(filter_json, projection, sort=sort_json, session=self.session)

        return collection.find_one(filter_json, projection, session=self.session)

    def delete_one_doc(self, db_name: str, collection_name: str, filter_json: dict, session=None):
        """
        Deletes only first matching document from the specified collection by applying the filter passed in the
        filter_json.
        :param db_name:
        :param collection_name:
        :param filter_json:
        :param session:
        :return:
        """
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        result = collection.delete_one(filter_json, session=self.session)
        return result.deleted_count

    def find_distinct_fields(self, db_name: str, collection_name: str, distinct_key: str, filter_json: dict = None):
        """
        Finds distinct entries of the key based on the filter passed.
        :param db_name:
        :param collection_name:
        :param distinct_key:
        :param filter_json:
        :return:
        """
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        return collection.distinct(distinct_key, filter=filter_json)

    def aggregate_docs(self, db_name: str, collection_name: str, aggregate_filter: list, session=None, collation={}):
        """
        Unwind Nested Array and Match condition passed and Project in specified collection.
        :param db_name:
        :param collection_name:
        :param aggregate_filter:
        :param session:
        :return:
        """
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        return collection.aggregate(aggregate_filter, session=self.session, collation=collation)

    def delete_docs(self, db_name: str, collection_name: str, filter_json: dict, session=None):
        """
        Deletes matching documents from the specified collection by applying the filter passed in the filter_json.
        :param db_name:
        :param collection_name:
        :param filter_json:
        :param session:
        :return:
        """
        db = self.get_pymongo_db(db_name)
        collection = db[collection_name]
        result = collection.delete_many(filter_json, session=self.session)
        return result.deleted_count


