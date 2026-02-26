from datetime import date, time
from tinydb_serialization import Serializer

# 1. Serializer für Datum
class DateSerializer(Serializer):
    OBJ_CLASS = date
    
    def encode(self, obj):
        return obj.isoformat()
        
    def decode(self, s):
        return date.fromisoformat(s)

# 2. Serializer für Uhrzeit
class TimeSerializer(Serializer):
    OBJ_CLASS = time
    
    def encode(self, obj):
        return obj.isoformat(timespec='minutes')
        
    def decode(self, s):
        return time.fromisoformat(s)