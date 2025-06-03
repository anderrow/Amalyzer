from fastapi import APIRouter
from backend.memory.state import session_data
from backend.classes.db_connection import DBConnection
from backend.database.config import config
from backend.classes.request import RequestPropId
from backend.database.query import query_valuable_information

router = APIRouter(prefix="/common")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py   

# ---------- Get Actual PropId to analyze ---------- #
@router.get("/PropId")
async def analyzer_status():
    current_prop = RequestPropId().return_data()
    return current_prop

# ---------- Extra Information from the PropId ---------- #
@router.get("/PropIdExtraInfo")
async def analyzer_status():
    data = await fetch_data(query_valuable_information)

    if data and isinstance(data, list) and isinstance(data[0], dict):
        values = list(data[0].values())  # ['Vitacell R200', 'MIAVIT 174240##Vitacell R200'] (Extract values from dict)
        formatted = " | ".join(values)   # 'Vitacell R200 | MIAVIT 174240##Vitacell R200' 
        
        return formatted
    return


# ---------- Request data for table  ---------- #
async def fetch_data(query_template: str):
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_template.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}