import os
from datetime import date, time
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb_serialization import SerializationMiddleware
from .serializer import DateSerializer, TimeSerializer

class DatabaseConnector:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
            serialization = SerializationMiddleware(JSONStorage)
            serialization.register_serializer(DateSerializer(), 'TinyDate')
            serialization.register_serializer(TimeSerializer(), 'TinyTime')
            cls._instance.db = TinyDB(cls._instance.path, storage=serialization)
            
        return cls._instance
    
    def get_table(self, table_name: str):
        return self.db.table(table_name)