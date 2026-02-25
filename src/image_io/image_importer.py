import numpy as np
from PIL import Image

class ImageImporter:
    
    @staticmethod
    def create_mask(input_data, threshold=128, dark_is_material=False):
        """        
        Konvertiert Bilddaten in ein 2D-Array (0 und 1).
        Akzeptiert Dateipfade (str), Streamlit UploadedFile Objekte ODER NumPy Arrays (vom Canvas).
        Schneidet leere Ränder automatisch ab. -> "Bounding Box"
        """
        try:
            # Bilddaten einlesen und vorbereiten
            if isinstance(input_data, np.ndarray):
                # wenn es schon ein Array ist (von Canvas)
                if len(input_data.shape) == 3 and input_data.shape[2] >= 3:
                    # RGBA zu Graustufen konvertieren durch Mittelwert der RGB-Kanäle
                    img_array = np.mean(input_data[:, :, :3], axis=2)
                else:
                    img_array = input_data
            else:
                # Standard-Weg: Image.open verarbeitet Streamlit Buffer oder Dateipfade
                img = Image.open(input_data).convert('L')
                img_array = np.array(img)
            
            # Maske erstellen
            mask = np.zeros_like(img_array, dtype=int)
            
            if dark_is_material:
                mask[img_array < threshold] = 1
            else:
                mask[img_array >= threshold] = 1
                
            # Zuschnitt auf "Bounding Box"
            active_rows = np.any(mask > 0, axis=1)
            active_cols = np.any(mask > 0, axis=0)
            
            if np.any(active_rows) and np.any(active_cols):
                ymin, ymax = np.where(active_rows)[0][[0, -1]]
                xmin, xmax = np.where(active_cols)[0][[0, -1]]
                mask = mask[ymin:ymax+1, xmin:xmax+1]
            else:
                # falls das Bild leer ist
                return None
                
            return mask
            
        # Fehlerbehandlung
        except Exception as e:
            print(f"Fehler beim Bildimport: {e}")
            return None
        
    