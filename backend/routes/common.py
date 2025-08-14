from fastapi import APIRouter, Request
from backend.classes.db_connection import DBConnection
from backend.classes.request import RequestPropId
from backend.database.query import query_valuable_information
from backend.classes.request import RequestEnvironment
from backend.database.db_connections import ALL_DB_CONNECTIONS

router = APIRouter(prefix="/common")  

# ---------- Get Actual PropId to analyze ---------- #
@router.get("/PropId")
async def analyzer_status(request: Request):# Get the current proportioning ID from the request cookies
    current_prop = RequestPropId(request).return_data()
    current_env = RequestEnvironment(request).return_data()
    if current_env is None or current_env == "None":
        current_env = "Default"
    return str(current_prop) + " | " + str(current_env)

# ---------- Extra Information from the PropId ---------- #
@router.get("/PropIdExtraInfo")
async def analyzer_status(request: Request):  # Get the current proportioning ID from the request cookies 
    db_connection = connect_to_user_environment(request)

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
def connect_to_user_environment(request):
    # Get configuration based on the user's environment
    env_key  = (RequestEnvironment(request).return_data())
    
    if env_key is None or env_key not in ALL_DB_CONNECTIONS:
        print(f"Environment (not) defined as {env_key},  using default configuration.")
        env_key = "CONFIG"  # Default key for DB Connection
    
    # Initialize the DBConnection object with the selected environment
    return  ALL_DB_CONNECTIONS[env_key]