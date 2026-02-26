from core.structure import Structure
from core.elements import Spring, Node
import numpy as np

class StructureBuilder:
    """
    Builder-Klasse zum Erstellen von verschiedenen Strukturen
    """
    @staticmethod
    def _connect_neighbors(structure, node_map):
        """
        Hilfsmethode: verbindet benachbarte Knoten mit Federn
        """
        # Verbindungen erstellen: alle 8 Nachbarn (wenn vorhanden)
        neighbor_offsets = [
            (-1, -1), (-1,  0), (-1,  1),
            ( 0, -1),           ( 0,  1),
            ( 1, -1), ( 1,  0), ( 1,  1),
        ]
        
        # iterieren nur über tatsächlich vorhandene Knoten in der Map
        for (i, j), current_id in node_map.items():
            for di, dj in neighbor_offsets:
                ni, nj = i + di, j + dj
                
                # Prüfen, ob der errechnete Nachbar existiert
                if (ni, nj) in node_map:
                    neighbor_id = node_map[(ni, nj)]
                    
                    # Nur verbinden, wenn Nachbar-ID größer -> vermeidet Doppelte
                    if neighbor_id > current_id:
                        node_i = structure.get_node(current_id)
                        node_j = structure.get_node(neighbor_id)
                        spring_obj = Spring(node_i, node_j)
                        structure.add_spring(current_id, neighbor_id, spring_obj)

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
        
        # Nachbarknoten mit Federn verbinden
        StructureBuilder._connect_neighbors(structure, node_map)
        
        return structure
    
    @staticmethod
    def create_from_mask(mask_2d_array, element_length=1.0):
        """
        Erstellt eine Struktur basierend auf einer 2D-Maske.
        1 (oder Werte > 0) = Knoten/Material, 0 = Leer/Loch.
        """
        structure = Structure()
        mask = np.array(mask_2d_array)
        
        # Dimensionen der Maske auslesen
        n_points_h, n_points_w = mask.shape
        
        node_id = 0
        node_map = {}  # speichert (i,j) -> node_id mapping
        
        # Über Grid von Punkten iterieren und Material Knoten erstellen
        for i in range(n_points_h):
            for j in range(n_points_w):
                if mask[i, j] > 0:  # Nur erstellen, wo Material definiert ist
                    x = j * element_length
                    y = i * element_length
                    
                    node_obj = Node(node_id=node_id, pos=np.array([x, y]))
                    structure.add_node(node_id, node_obj)
                    node_map[(i, j)] = node_id
                    node_id += 1
        
        # Nachbarknoten mit Federn verbinden
        StructureBuilder._connect_neighbors(structure, node_map)
                        
        return structure