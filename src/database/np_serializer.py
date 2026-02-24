import numpy as np
import json
from tinydb_serialization import Serializer

class NumpyArraySerializer(Serializer):
    """
    Erlaubt das Speichern von NumPy Arrays in TinyDB.
    Wandelt np.array -> JSON-String (beim Speichern)
    Wandelt JSON-String -> np.array (beim Laden)
    """
    OBJ_CLASS = np.ndarray  # Dieser Serializer springt an, wenn er ein np.ndarray sieht

    def encode(self, obj):
        # 1. Numpy Array in Liste umwandeln
        # 2. Liste in JSON-String umwandeln (WICHTIG!)
        return json.dumps(obj.tolist())

    def decode(self, s):
        # 1. JSON-String zurück in Liste wandeln
        # 2. Liste in Numpy Array wandeln
        return np.array(json.loads(s))