from fastapi import APIRouter
from fastapi import Query
from backend.classes.db_connection import DBConnection
from backend.classes.filter_data import FilterByString, FilterByDateTime
from backend.classes.request import PropIdRequest
from backend.database.config import config
from backend.database.query import query_proportionings
from backend.classes.calculation import CalculateDate
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum

# Create an APIRouter instance
router = APIRouter()

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

# SQL query to fetch proportioning data
query = query_proportionings #query is declared in backend/database/query.py


# ----------------- GET endpoint to retrieve proportioning data (Controls -> Update button) -----------------
@router.get("/api/proportionings")
async def get_proportionings() -> List[Dict[str, Any]]:
    try:
        # Fetch data from the database
        data = await db_connection.fetch_data(query=query) #Raw Data
        #Overwrite Endtime with EndTime - StartTime to calculate duration
        data = CalculateDate(data, "StartTime", "EndTime", overwrite=True).apply_calculation()
        return make_db_redable(data) #Return data after making it redable for the user

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ----------------- GET endpoint to retrieve proportioning filtered data (Controls -> Update Filtered Data button) -----------------
@router.get("/api/proportioningsfilter") #Article + Age Filter -> Update Filtered Data Button
async def get_proportionings_filtered(
    switchChecked: bool = Query(False),  # Default is False (switch off)
    requestedArticle: str = Query(""), # Default is empty string if no input
    ageSwitchChecked: bool = Query(False),  # Parameter for Age Filter switch (Default False)
    timeUnit: str = Query("Minutes"),  # Parameter for time unit (minutes, hours, days) (Default Minutes)
    rangeValue: int = Query(50)  # Parameter for slider value (default to 50)  
) -> List[Dict[str, Any]]:
    try:
        # Fetch data from the database
        data = await db_connection.fetch_data(query=query)
        data = CalculateDate(data, "StartTime", "EndTime", overwrite=True).apply_calculation()

        #Filter by Article if it's requested
        if switchChecked:
            data = FilterByString(data, requestedArticle, 'ArticleName').apply_filter()
            print("\n"+"*"*50 +"\nArticle Filter Switch enabled")
            print(f"Requested Article: {requestedArticle} \n"+"*"*50+"\n")
            
            
        # Handle Age Filter logic
        if ageSwitchChecked:
            # Filter by age range if needed based on rangeValue and timeUnit
            data = FilterByDateTime(data, rangeValue, timeUnit, 'StartTime').apply_filter()
            print("\n" + "*" * 50 + "\nAge Filter Switch enabled")
            print(f"Requested Time: {rangeValue} {timeUnit} \n" + "*" * 50 + "\n")
        
        return make_db_redable(data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}  




# ----------------- Define a POST route that listens for row click events from the frontend ----------------- 
@router.post("/api/rowclicked")
async def handle_row_click(request: PropIdRequest):
    # Print the received propDbId to the backend console for debugging/logging purposes
    print("\n"+ "*"*50 + f"\nPropDBID selected: {request.propDbId} \n"+ "*"*50+"\n")
    
    return {"message": f"Received PropDBID: {request.propDbId}"} # Return a confirmation message as a JSON response (Not mandatory for now)



#Filter Database to make it more redable
class DosingType(Enum):
    NORMAL = 1
    LEARNING = 2
    D2E = 100

def make_db_redable(data):
    for row in data:
            # Format the "StartTime" field if it's a datetime object
            if "StartTime" in row and isinstance(row["StartTime"], datetime):
                dt = row["StartTime"]
                formatted_start = f"{dt.year}-{dt.strftime('%m')}-{dt.strftime('%d')} {dt.strftime('%A')} {dt.strftime('%H:%M:%S')}"
                row["StartTime"] = formatted_start

            # Format the "Actual" field to 4 decimal places if it's a number
            if "Actual" in row and isinstance(row["Actual"], (float, int)):
                row["Actual"] = round(row["Actual"], 4)

            # Convert boolean VMSscan to emojis
            if "VMSscan" in row and isinstance(row["VMSscan"], bool):
                row["VMSscan"] = "✅" if row["VMSscan"] else "❌"
            # Change the Formato of Lot ID
            if "LotID" in row and isinstance(row["LotID"], str):
                row["LotID"] = row["LotID"].replace("##", "#<br>#") #<br> works better than \n 

            # Change the Formato of Lot ID
            if "TypeOfDosing" in row and isinstance(row["TypeOfDosing"], int):
                value = row["TypeOfDosing"]
                try:
                    row["TypeOfDosing"] = DosingType(value).name.capitalize()
                except ValueError:
                    row["TypeOfDosing"] = f"Unknown ({value})"
                
    return data


