from .db_connector import DatabaseConnector

def save_input_to_table(length, width):
        """Speichert die Eingabedaten in Tabelle mit dem Name 'inputdata' und gibt die ID des neuen Eintrags zurück."""
        db = DatabaseConnector()
        table = db.get_table('inputdata')
        
        input_data = {
            "length": float(length),
            "width": float(width),
            "status": "new",
        }
        
        # insert, da hier neuer Eintrag erstellt wird und den session.state.current_calc_id für die Berechnung bestimmt und zurückgibt
        return table.insert(input_data)

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
    """Holt alle Daten zu einer spezifischen Berechnungs-ID."""
    db = DatabaseConnector()
    table = db.get_table("inputdata")
    return table.get(doc_id=calc_id)

def save_optimization_state(calc_id: int, state_dict: dict, opt_type: str):
    """Speichert den aktuellen Status der Optimierung in der Datenbank."""
    db = DatabaseConnector()
    table = db.get_table("inputdata")

    update_data = {
        "saved_opt_state": state_dict,
        "saved_opt_type": opt_type
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



