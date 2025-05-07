from pydantic import BaseModel
from backend.memory.state import session_data
from backend.database.query import query_lot_db_id
from backend.classes.db_connection import DBConnection
from backend.database.config import config

# Import BaseModel from Pydantic to define the expected structure of the request body
class PropIdRequest(BaseModel):
    # This field represents the ID of the selected row, expected to be an integer
    propDbId: int

class Request:
        def __init__(self):        
            #Get current proportioning id
            self.current_prop = session_data.get("current_prop_id")

        def return_data(self):
            raise NotImplementedError("Subclasses should implement this method.")

class RequestPropId(Request):
    def __init__(self):

        super().__init__()

    def return_data(self):
        data = self.current_prop
        return data

class RequestLotId(Request):
    
    def __init__(self):
        
        super().__init__()

    async def return_data(self):
        # Initialize the DBConnection object
        db_connection = DBConnection(config=config) #config is declared in backend/database/config.py
        #Write the current_prop variable inside the query
        query = query_lot_db_id.format(current_prop=self.current_prop)
        #Save lot_id
        lot_id = await db_connection.fetch_data(query=query)
        #Extract the lot_id
        data = lot_id[0]["lot_dbid"]    
        return data
