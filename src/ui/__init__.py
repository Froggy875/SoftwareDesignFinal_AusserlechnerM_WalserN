import st_ui
import components
from src.database.db_connector import DatabaseConnector

if __name__ == "__main__":
    database = DatabaseConnector().get_table("calculations")
    st_ui.main()