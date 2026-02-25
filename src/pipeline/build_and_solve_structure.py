import numpy as np
from core.structureBuilder import StructureBuilder
from core.solver import solve

def build_and_solve_structure(calc_data):
    length = calc_data['length']
    width = calc_data['width']
    fixed_points = calc_data['fixed_points']
    roller_points = calc_data['roller_points']
    forces_data = calc_data['forces_data']

    # Struktur erstellen
    structure = StructureBuilder.create_rectangle(n_points_w=int(length), n_points_h=int(width))

    # --PROVISORIUM ZUM BILDER HOCHLADEN-- 
    # Puffer-Maske aus dem Dictionary holen ...falls vorhanden
    mask = calc_data.get('mask', None)

    # Struktur erstellen
    if mask is not None:
        # Bild in Struktur umwandeln
        structure = StructureBuilder.create_from_mask(mask) 
    else:
        # Standard Weg für manuell eingegebene Maße
        structure = StructureBuilder.create_rectangle(n_points_w=int(length), n_points_h=int(width))
    # --PROVISORIUM ENDE--


    """ def get_node_id(x, y):
        return int(y) * length + int(x)

    # Festlager setzen
    for pt in fixed_points:
        node_id = get_node_id(pt[0], pt[1])
        structure.get_node(node_id).fixed = [True, True]

    # Rollenlager setzen
    for pt in roller_points:
        node_id = get_node_id(pt[0], pt[1])
        structure.get_node(node_id).fixed = [False, True]
    
    # Kräfte setzen
    for pt_key, force_vector in forces_data.items():
        x_str, y_str = pt_key.split('_')
        node_id = get_node_id(int(x_str), int(y_str))
        structure.get_node(node_id).force = np.array(force_vector)

    # Berechnung durchführen
    structure.solve()
    
    return structure """

    # --ANPASSUNG/VERBESSERUNG ZUM BILDER EINLESEN-- 
    def get_node_by_coords(x, y):
        for node_id in structure.get_nodes():
            node = structure.get_node(node_id)
            if node.pos[0] == x and node.pos[1] == y:
                return node
        return None

    # Festlager setzen
    for pt in fixed_points:
        node = get_node_by_coords(pt[0], pt[1])
        if node:
            node.fixed = [True, True]

    # Rollenlager setzen
    for pt in roller_points:
        node = get_node_by_coords(pt[0], pt[1])
        if node:
            node.fixed = [False, True]
    
    # Kräfte setzen
    for pt_key, force_vector in forces_data.items():
        x_str, y_str = pt_key.split('_')
        node = get_node_by_coords(int(x_str), int(y_str))
        if node:
            node.force = np.array(force_vector)
     # --ANPASSUNG/VERBESSERUNG ZUM BILDER EINLESEN ENDE--

    # Berechnung durchführen
    structure.solve()
    
    return structure