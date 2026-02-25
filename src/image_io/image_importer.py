import numpy as np
from PIL import Image

class ImageImporter:
    
    @staticmethod
    def create_mask(file_or_path, threshold=128, dark_is_material=False):
        """
        Liest ein Bild ein und konvertiert es in ein 2D-Array (0 und 1).
        Akzeptiert Dateipfade (str) oder Streamlit UploadedFile Objekte.
        """
        try:
            # Image.open verarbeitet Streamlit Buffer
            img = Image.open(file_or_path).convert('L')
            
            img_array = np.array(img)
            mask = np.zeros_like(img_array, dtype=int)
            
            if dark_is_material:
                mask[img_array < threshold] = 1
            else:
                mask[img_array >= threshold] = 1
                
            return mask
            
            # Fehlerbehandlung
        except Exception as e:
            print(f"Fehler beim Bildimport: {e}")
            return None
        
    