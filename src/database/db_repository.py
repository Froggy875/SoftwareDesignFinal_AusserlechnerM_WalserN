import os
import json
import numpy as np
from datetime import date, datetime
from .db_connector import DatabaseConnector


# Ordner definieren, in dem die npz-Dateien landen
MATRIX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'matrizen_daten')
os.makedirs(MATRIX_DIR, exist_ok=True)


def save_input_to_table(project_type,length, width, mask=None):
    """Speichert die Eingabedaten in TinyDB und die Maske als .npz-Datei."""
    db = DatabaseConnector()
    table = db.get_table('inputdata')
    input_data = {
        "project_type": project_type,
        "length": int(length),
        "width": int(width),
        "created_date": date.today(),
        "created_time": datetime.now().time()
    }
    
    # 1. Neuen Eintrag erstellen und die ID übernehmen
    calc_id = table.insert(input_data)
    
    # 2. Wenn eine Maske übergeben wurde, als .npz speichern
    if mask is not None:
        file_name = f"maske_{calc_id}.npz"
        file_path = os.path.join(MATRIX_DIR, file_name)
        # Matrix komprimiert speichern
        np.savez_compressed(file_path, mask_matrix=mask)
        # Der Datenbank mitteilen, wo die Datei liegt
        table.update({"mask_file": file_name}, doc_ids=[calc_id])
    
    return calc_id

def update_calculation_data(calc_id, fixed_points, roller_points, force_points, forces_data, mode=None, optimizer=None):
    '''Aktualisiert einen bestehenden Datenbankeintrag mit den restlichen Wizard-Daten.'''
    
    db = DatabaseConnector()
    table = db.get_table("inputdata")

    update_data = {
        "fixed_points": fixed_points,
        "roller_points": roller_points,
        "force_points": force_points,
        "forces_data": forces_data,
        "mode": mode,
        "optimizer": optimizer
    }
        
    # TinyDB updatet das Dokument mit der passenden ID
    table.update(update_data, doc_ids=[calc_id])
    
    return True

def get_calculation_data(calc_id: int) -> dict:
    """Holt alle Daten zu einer ID, inklusive der verknüpften Matrix."""

    if calc_id is None:
        return None
    
    db = DatabaseConnector()
    table = db.get_table("inputdata")
    
    # 1. Metadaten aus TinyDB holen
    data = table.get(doc_id=calc_id)
    
    if data is None:
        return None # Sicherheitscheck, falls ID nicht existiert
        
    # 2. Prüfen, ob eine Masken-Datei hinterlegt ist
    if "mask_file" in data:
        file_path = os.path.join(MATRIX_DIR, data["mask_file"])
        
        # 3. Datei laden und die Matrix nahtlos an das Dictionary anhängen
        if os.path.exists(file_path):
            geladene_npz = np.load(file_path)
            data["mask"] = geladene_npz["mask_matrix"]
        else:
            data["mask"] = None # Fallback, falls die Datei manuell gelöscht wurde

    #3. Prüfen, ob ein Optimierungsstand gespeichert ist
    if "opt_state_file" in data:
        file_path = os.path.join(MATRIX_DIR, data["opt_state_file"])
        if os.path.exists(file_path):
            geladene_npz = np.load(file_path)
            
            # string mit .item() holen
            json_string = geladene_npz["state_data"].item()
            # String wieder in ein Python Dictionary verwandeln
            data["saved_opt_state"] = json.loads(json_string)
        else:
            data["saved_opt_state"] = None
            
    return data

def save_optimization_state(calc_id: int, state_dict: dict, opt_type: str):
    """Speichert den aktuellen Status der Optimierung als NPZ."""
    db = DatabaseConnector()
    table = db.get_table("inputdata")

    # 1. Dictionary in einen flachen String verwandeln
    state_json_str = json.dumps(state_dict)

    # 2. Als NPZ speichern
    file_name = f"opt_state_{calc_id}.npz"
    file_path = os.path.join(MATRIX_DIR, file_name)
    np.savez_compressed(file_path, state_data=state_json_str)

    # 3. In TinyDB updaten
    update_data = {
        "saved_opt_state": True,
        "saved_opt_type": opt_type,
        "opt_state_file": file_name
    }
    table.update(update_data, doc_ids=[calc_id])
    
    return True

def delete_optimization_state(calc_id: int):
    """Löscht den gespeicherten Status der Optimierung in der Datenbank, 
    indem die entsprechenden Felder geleert werden."""
    db = DatabaseConnector()
    table = db.get_table("inputdata")

    # Felder auf None setzen, damit has_saved_state beim nächsten Laden False wird
    update_data = {
        "saved_opt_state": None,
        "saved_opt_type": None
    }
        
    table.update(update_data, doc_ids=[calc_id])
    
    return True



