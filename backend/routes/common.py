from fastapi import APIRouter, Request
from backend.classes.db_connection import DBConnection
from backend.database.config import config
from backend.classes.request import RequestPropId
from backend.database.query import query_valuable_information
from backend.classes.request import RequestEnvironment
from backend.database.config import *

router = APIRouter(prefix="/common")  

# ---------- Get Actual PropId to analyze ---------- #
@router.get("/PropId")
async def analyzer_status(request: Request):# Get the current proportioning ID from the request cookies
    current_prop = RequestPropId(request).return_data()
    return current_prop

# ---------- Extra Information from the PropId ---------- #
@router.get("/PropIdExtraInfo")
async def analyzer_status(request: Request):  # Get the current proportioning ID from the request cookies 
    # Connect to the user's environment
    db_connection = connect_to_user_environment(request, env_map) 

    current_prop = RequestPropId(request).return_data()

    data = await fetch_data(query_valuable_information, current_prop, db_connection)

    if data and isinstance(data, list) and isinstance(data[0], dict):
        values = list(data[0].values())  # ['Vitacell R200', 'MIAVIT 174240##Vitacell R200'] (Extract values from dict)
        formatted = " | ".join(values)   # 'Vitacell R200 | MIAVIT 174240##Vitacell R200' 
        
        return formatted
    return


# ---------- Request data for table  ---------- #
async def fetch_data(query_template: str, current_prop: int, db_connection: DBConnection) -> dict:
    try:
        #Write the current_prop variable inside the query
        query = query_template.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    
# ------------ Get the current Environment from the request cookies ---------- #
def connect_to_user_environment(request: Request, env_map):
    environment = RequestEnvironment(request).return_data()
    selected_env = env_map.get(environment.upper(), UFA) #Default to UFA if the environment is not found
    return DBConnection(selected_env)