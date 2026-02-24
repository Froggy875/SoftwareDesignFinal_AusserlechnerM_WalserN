import os
from tinydb import TinyDB
from tinydb.table import Table
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from .np_serializer import NumpyArraySerializer

class DatabaseConnector:

    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')

            middleware = SerializationMiddleware(JSONStorage)
            middleware.register_serializer(NumpyArraySerializer(), 'NumpyArray')

            cls._instance.serializer = middleware
            cls._instance.db = TinyDB(cls._instance.path, storage=middleware)
            
        return cls._instance
    
    def get_table(self, table_name: str) -> Table:
        return self.db.table(table_name)    