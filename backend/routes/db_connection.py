import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any
import asyncio

class DBConnection:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    # Method to connect to the PostgreSQL database asynchronously (asyncio + psycopg2)
    async def connect(self):
        try:
            # Create connection using the configuration dictionary
            conn = psycopg2.connect(
                dbname=self.config['ConnectionStrings']['Database'],
                user=self.config['ConnectionStrings']['UserID'],
                password=self.config['ConnectionStrings']['Password'],
                host=self.config['ConnectionStrings']['Server'],
                port=self.config['ConnectionStrings']['Port']
            )
            return conn
        except Exception as e:
            raise Exception(f"Error connecting to database: {e}")

    # Method to execute a query and fetch results
    async def fetch_data(self, query: str) -> List[Dict[str, Any]]:
        conn = await self.connect()
        try:
            # Creating a cursor to execute SQL query
            cur = conn.cursor()

            # Execute the SQL query
            cur.execute(query)
            rows = cur.fetchall()

            # Get column names
            columns = [desc[0] for desc in cur.description]

            data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)

            # Close cursor and connection
            cur.close()
            conn.close()
            return data
        except Exception as e:
            raise Exception(f"Error executing query: {e}")
