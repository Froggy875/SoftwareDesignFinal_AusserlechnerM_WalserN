from database.db_repository import get_calculation_data
from pipeline.build_and_solve_structure import build_and_solve_structure

def get_prepared_structure(calc_id: int):
    """
    Lädt die Daten aus der Datenbank und baut die fertige Basis-Struktur.
    """
    calc_data = get_calculation_data(calc_id)
    structure = build_and_solve_structure(calc_data)
    
    return structure, calc_data