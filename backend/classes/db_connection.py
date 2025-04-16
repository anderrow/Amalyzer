import psycopg2
from typing import List, Dict, Any
import asyncio


class DBConnection:
    
    """
    Given a configuration dictionary (dbname, user, password, host, port [str, Any])
    provided at instantiation, and a SQL query passed to the fetch_data method, the 
    class returns a data dictionary containing the results of the requested query. 
    It is recommended to use the await keyword when calling fetch_data.
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

