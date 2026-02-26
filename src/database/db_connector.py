import os
from tinydb import TinyDB

class DatabaseConnector:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            
            cls._instance.path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')
            cls._instance.db = TinyDB(cls._instance.path)
            
        return cls._instance
    
    def get_table(self, table_name: str):
        return self.db.table(table_name)