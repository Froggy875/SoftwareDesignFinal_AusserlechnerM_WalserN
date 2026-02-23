import numpy as np
from tinydb_serialization import Serializer

class NumpyArraySerializer(Serializer):
    """
    Erlaubt das Speichern von NumPy Arrays in TinyDB.
    Wandelt np.array -> list (beim Speichern)
    Wandelt list -> np.array (beim Laden)
    """
    OBJ_CLASS = np.ndarray  # Dieser Serializer springt an, wenn er ein np.ndarray sieht

    def encode(self, obj):
        # Numpy Array in eine normale Python-Liste umwandeln
        return obj.tolist()

    def decode(self, s):
        # Liste zurück in ein Numpy Array wandeln
        return np.array(s)