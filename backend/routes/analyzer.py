# backend/routes/analyzer.py
from fastapi import APIRouter
from backend.memory.state import session_data
from backend.classes.db_connection import DBConnection
from backend.database.config import config
from backend.database.query import query_analyzer_summary
# Create an APIRouter instance
router = APIRouter(prefix="/analyzer")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

# Get Actual PropId to analyze
@router.get("/PropId")
async def analyzer_status():
    current_prop = session_data.get("current_prop_id")
    return current_prop

# Get Actual PropId to analyze
@router.get("/PropIdSummary")
async def analyzer_status():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_summary.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)

        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    
    
