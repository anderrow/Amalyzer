from backend.database.config import * # Import all configurations from config.py
from backend.classes.db_connection import DBConnection


ALL_DB_CONNECTIONS = {
    env_name: DBConnection(config) for env_name, config in env_map.items()
}

