from typing import Optional
from pydantic import BaseModel
from fastapi import Request
from backend.memory.state import session_data
from backend.database.query import query_lot_db_id
from backend.classes.db_connection import DBConnection
from backend.database.config import *


# Import BaseModel from Pydantic to define the expected structure of the request body
class UserInfo(BaseModel):
    propDbId: Optional[int] = None  # Include propDbId in the request model for tracking purposes
    uid: str  # Include UID in the request model for tracking purposes
    environment: str = "config"  # Optional field for environment, default is config 

class RequestBase:
    """
    Base class for handling user-specific requests in the application.
    Extracts the user UID from the request cookies and provides a template
    for subclasses to implement data retrieval methods based on the user's session.
    """
    def __init__(self, request: Request):  

        # Get the UID from the request cookies
        self.uid = request.cookies.get("uid") 
        

    def return_data(self):
        raise NotImplementedError(f"Subclasses should implement this method. Call one of: {[cls.__name__ for cls in RequestBase.__subclasses__()]}")


class RequestPropId(RequestBase):
    """
    When this class is called, it will return the current Proportioning ID attached to the user's UID.

    This class retrieves the current proportioning ID (current_prop_id) from the session data,
    which is associated with the user's UID extracted from the request cookies. The proportioning ID
    represents the currently selected or active proportioning record for the user session.
    """
    def __init__(self, uid: str):
        super().__init__(uid)

    def return_data(self):
        # Get current proportioning id for this user UID
        user_session = session_data.get(self.uid, {})
        current_prop = user_session.get("current_prop_id")
        
        if current_prop is not None:
            print("*"*75)
            print(f"* UID {self.uid} requested proportioning: {current_prop:<6}*")
            print("*"*75)

        return current_prop

class RequestLotId(RequestBase):
    """
    When this class is called, it will return the Lot Id attached to the current Proportioning ID
    """
    def __init__(self, uid: str):     
        super().__init__(uid)

    async def return_data(self):
        # Get current proportioning id for this user UID
        user_session = session_data.get(self.uid, {})
        current_prop = user_session.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_lot_db_id.format(current_prop=current_prop)

        # Initialize the DBConnection object
        db_connection = DBConnection(config=config) #config is declared in backend/database/config.py
        lot_id = await db_connection.fetch_data(query)  #Save lot_id
        data = lot_id[0]["lot_dbid"]    #Extract the lot_id

        if lot_id is not None:
            print("*"*69)
            print(f"* UID {self.uid} requested lot id: {data:<7}*")
            print("*"*69) # Debugging output  

        return data
class RequestEnvironment(RequestBase):
    """
    When this class is called, it will return the Environment attached to the current Proportioning ID
    """
    def __init__(self, uid: str):
        super().__init__(uid)

    def return_data(self):
        # Get current environment for this user UID
        user_session = session_data.get(self.uid, {})
        environment = user_session.get("environment")  # Default to "UFA" if not set

        if environment is not None:
            print("*"*75)
            print(f"* UID {self.uid} requested environment: {environment:<6}*")
            print("*"*75)

        return str(environment)
    
    @staticmethod
    def connect_to_user_environment(request: Request) -> DBConnection:
        environment = RequestEnvironment(request).return_data()
        selected_env = env_map.get(environment.upper(), config) #Default to config if the environment is not found 
        return DBConnection(selected_env)