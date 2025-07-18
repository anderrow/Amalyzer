import psycopg2
from typing import List, Dict, Any
import asyncio
import pandas as pd
from sqlalchemy import create_engine

class DBConnection:
    """
    Handles the connection to the database. Provides methods to connect, disconnect, and manage
    the database session or cursor. Intended to be used as a utility class for database operations.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    # Synchronous method to handle connection and query execution
    def _connect_and_fetch(self, query: str) -> List[Dict[str, Any]]:
        try:
            # Establish a connection using the config dictionary
            conn = psycopg2.connect(
                dbname=self.config['ConnectionStrings']['Database'],
                user=self.config['ConnectionStrings']['UserID'],
                password=self.config['ConnectionStrings']['Password'],
                host=self.config['ConnectionStrings']['Server'],
                port=self.config['ConnectionStrings']['Port']
            )

            # Create a cursor and execute the query
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()

            # Extract column names
            columns = [desc[0] for desc in cur.description]

            # Combine columns and row data into a list of dictionaries
            data = [dict(zip(columns, row)) for row in rows]

            # Clean up
            cur.close()
            conn.close()

            return data
        except Exception as e:
            raise Exception(f"Error executing query: {e}")

    # Asynchronous method that runs the blocking code in a separate thread
    async def fetch_data(self, query: str) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._connect_and_fetch, query)
    
    def _connect_and_fetch_df(self, query: str, current_prop =None) -> pd.DataFrame:
        try:
            # Build SQLAlchemy connection string
            user = self.config['ConnectionStrings']['UserID']
            password = self.config['ConnectionStrings']['Password']
            host = self.config['ConnectionStrings']['Server']
            port = self.config['ConnectionStrings']['Port']
            dbname = self.config['ConnectionStrings']['Database']

            # Example: postgresql+psycopg2://user:password@host:port/dbname
            connection_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
            engine = create_engine(connection_str)

            query = query.format(current_prop=current_prop)

            # Read query into pandas DataFrame
            df = pd.read_sql(query, engine)

            # Dispose the SQLAlchemy engine to clean up resources
            engine.dispose()

            return df

        except Exception as e:
            raise Exception(f"Error executing query: {e}")
        
     # Asynchronous method that runs the blocking code in a separate thread   
    async def fetch_df(self, query: str, current_prop=None) -> pd.DataFrame:
        return await asyncio.to_thread(self._connect_and_fetch_df, query, current_prop)

class DBConnectionError(Exception):
    """
    Custom exception for database connection errors. Raised when a connection or query fails.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)