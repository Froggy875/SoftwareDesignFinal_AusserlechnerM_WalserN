from core.structure import Structure
from core.elements import Spring, Node
import numpy as np

class StructureBuilder:
    """
    Builder-Klasse zum Erstellen von verschiedenen Strukturen
    """
    
    @staticmethod
    # Statische Methode, damit für das Erstellen kein Builder-Objekt instanziiert werden muss 
    # ...und kein Zugriff über 'self' nötig ist
    def create_rectangle(n_points_w, n_points_h, element_length=1.0):
        """
        Erstellt ein Rechteck-Gitter basierend auf einer festen Elementlänge
        element_length zum sicherstellen, dass alle Zellen quadratisch sind
        """
        structure = Structure()
        
        # Grid von Punkten erstellen
        node_id = 0
        node_map = {}  # speichert (i,j) -> node_id mapping
        
        for i in range(n_points_h):
            for j in range(n_points_w):
                x = j * element_length
                y = i * element_length
                
                node_obj = Node(node_id=node_id, pos=np.array([x, y]))
                structure.add_node(node_id, node_obj)
                node_map[(i, j)] = node_id
                node_id += 1
        
        # Verbindungen erstellen: alle 8 Nachbarn (wenn vorhanden)
        neighbor_offsets = [
            (-1, -1), (-1,  0), (-1,  1),
            ( 0, -1),           ( 0,  1),
            ( 1, -1), ( 1,  0), ( 1,  1),
        ]
        
        for i in range(n_points_h):
            for j in range(n_points_w):
                current_id = node_map[(i, j)]
                
                for di, dj in neighbor_offsets:
                    ni, nj = i + di, j + dj
                    
                    if 0 <= ni < n_points_h and 0 <= nj < n_points_w:
                        neighbor_id = node_map[(ni, nj)]
                        
                        # Nur verbinden, wenn Nachbar-ID größer (vermeidet Dopplungen)
                        if neighbor_id > current_id:
                            node_i = structure.get_node(current_id)
                            node_j = structure.get_node(neighbor_id)
                            spring_obj = Spring(node_i, node_j)
                            structure.add_spring(current_id, neighbor_id, spring_obj)
        
        return structure