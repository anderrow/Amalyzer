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
        self.engine = None
        
        
    def _get_engine(self):
        """
        Generate an engine if doesn't exist, it return it for future use
        """
        
        if self.engine is None:
            if self.engine is None:
                user = self.config['ConnectionStrings']['UserID']
                password = self.config['ConnectionStrings']['Password']
                host = self.config['ConnectionStrings']['Server']
                port = self.config['ConnectionStrings']['Port']
                dbname = self.config['ConnectionStrings']['Database']
                connection_str = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}" # String for SQLAlchemy engine
                self.engine = create_engine(connection_str, pool_pre_ping=True) #Pool pre ping to avoid disconnections (it checks if the connection is alive before using it)
        
        return self.engine
    
    def _connect_and_fetch_df(self, query: str, current_prop =None) -> pd.DataFrame:
        try:
            engine = self._get_engine() # Get or create the SQLAlchemy engine
            
            if current_prop is not None:
                query = query.format(current_prop=current_prop) # Format the query with current_prop if provided

            return pd.read_sql(query, engine) # Use pandas to execute the query and return a DataFrame
        
        except Exception as e:
            raise Exception(f"Error executing query: {e}")

    def _connect_and_fetch(self, query: str) -> List[Dict[str, Any]]:
        try:
            df = self._connect_and_fetch_df(query)
            return df.to_dict(orient='records')
        
        except Exception as e:
            raise Exception(f"Error executing query: {e}")

    
    def close(self):
        """
        Close the engine and all its connections if it exists.
        """
        if self.engine:
            self.engine.dispose()
            self.engine = None
    
    # Asynchronous method that runs the blocking code in a separate thread
    async def fetch_data(self, query: str) -> List[Dict[str, Any]]:
        return await asyncio.to_thread(self._connect_and_fetch, query)      
    # Asynchronous method that runs the blocking code in a separate thread   
    async def fetch_df(self, query: str, current_prop=None) -> pd.DataFrame:
        return await asyncio.to_thread(self._connect_and_fetch_df, query, current_prop)
