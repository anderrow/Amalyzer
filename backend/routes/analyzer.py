from fastapi import APIRouter
from backend.memory.state import session_data
from backend.classes.db_connection import DBConnection
from backend.database.config import config
from backend.database.query import query_analyzer_summary, query_analyzer_propRecord, query_analyzer_logginParam, query_analyzer_lot, query_analyzer_article
# Create an APIRouter instance
router = APIRouter(prefix="/analyzer")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

# Get Actual PropId to analyze
@router.get("/PropId")
async def analyzer_status():
    current_prop = session_data.get("current_prop_id")
    return current_prop

# ---------- SUMMARY TABLE ---------- #
@router.get("/Summary")
async def summary_table():
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

# ---------- PROP RECORD ---------- #    
@router.get("/PropRecord")
async def propRecord_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_propRecord.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ---------- Logging Param ---------- #    
@router.get("/LogginParam")
async def propRecord_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_logginParam.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ---------- Logging Param ---------- #    
@router.get("/Lot")
async def lot_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_lot.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    
# ---------- Logging Param ---------- #    
@router.get("/Article")
async def article_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_article.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}