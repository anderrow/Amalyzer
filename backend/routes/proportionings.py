from fastapi import APIRouter
from fastapi import Query
from backend.database.config import config
from backend.database.query import query_proportionings
from backend.classes.db_connection import DBConnection
from backend.classes.filter_data import FilterByString, FilterByDateTime
from backend.classes.request import PropIdRequest
from backend.classes.calculation import CaclulateDateDelta, CaclulatPercent, IsInTolerance
from backend.memory.state import session_data
from typing import List, Dict, Any
from datetime import datetime
from enum import Enum
import pandas as pd

# Create an APIRouter instance
router = APIRouter()

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

# ----------------- GET endpoint to retrieve proportioning data (Controls -> Update button) ----------------- #

@router.get("/api/proportionings")
async def get_proportionings() -> List[Dict[str, Any]]:
    try:
        # Fetch data from the database
        data = await db_connection.fetch_data(query=query_proportionings) #Raw Data

        #Make all the calculations that are needed
        data = calculate(data)

        return make_db_redable(data) #Return data after making it redable for the user

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ----------------- GET endpoint to retrieve proportioning filtered data (Controls -> Update Filtered Data button) ----------------- #

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
        data = await db_connection.fetch_data(query=query_proportionings)

        #Make all the calculations that are needed
        data = calculate(data)

        #Filter by Article if it's requested
        if switchChecked:
            data = FilterByString(data, requestedArticle, 'ArticleName').apply_filter()
            print("\n"+"*"*50 +"\n* Article Filter Switch enabled" + " "*18 + "*")
            print(f"* Requested Article: {requestedArticle:<28}* \n"+"*"*50+"\n")
            
            
        # Handle Age Filter logic
        if ageSwitchChecked:
            # Filter by age range if needed based on rangeValue and timeUnit
            data = FilterByDateTime(data, rangeValue, timeUnit, 'StartTime').apply_filter()
            print("\n" + "*" * 50 + "\n* Age Filter Switch enabled" + " "*22 + "*")
            print(f"* Requested Time: {rangeValue} {timeUnit:<28}* \n" + "*" * 50 + "\n")
        
        return make_db_redable(data)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}  


# ----------------- Define a POST route that listens for row click events from the frontend ----------------- #
@router.post("/api/rowclicked")
async def handle_row_click(request: PropIdRequest):
    # Print the received propDbId to the backend console for debugging/logging purposes
    print("\n"+ "*"*50+ "\n" + f"* PropDBID selected: {request.propDbId:<28}*"+ "\n" + "*"*50 + "\n")
    # Save int he dictionary using current_prop_id keyword
    session_data["current_prop_id"] = request.propDbId
    return {"propDbId": request.propDbId} # Return a confirmation message as a JSON response (Not mandatory for now)

# ----------------- Request all the article names ----------------- #
@router.get("/api/articlenames")
async def get_article_names() -> List[Dict[str, Any]]:
    try:
        # Fetch data from the database
        data = await db_connection.fetch_data(query=query_proportionings)   
        # Convert the data to a pandas DateFrame
        df = pd.DataFrame(data)
        #Get unique values from the 'ArticleName' column
        unique_article_names =df['ArticleName'].unique()
        # Create a list of dictionaries (required format)
        result = [{"ArticleName": name} for name in unique_article_names]
        #Return the results
        return result

    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}  

# ----------------- Make all the calculations that are needed ----------------- #
def calculate(data):
    #Overwrite Endtime with EndTime - StartTime to calculate duration
    data = CaclulateDateDelta(data, "StartTime", "EndTime", overwrite=True).apply_calculation()
    #Add percentage calculation column
    data = CaclulatPercent(data, "Requested", "Tolerance", overwrite=False).apply_calculation()
    #Add deviation column
    data = IsInTolerance(data, "Requested", "Actual", "Tolerance").apply_calculation()

    return data
#  -----------------  Filter Database to make it more redable  ----------------- #
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

            # Format the "Tolerance" column
            if ("Tolerance" in row and isinstance(row["Tolerance"], float) and "calc_per" in row and isinstance(row["calc_per"], float)):
                row["Tolerance"] = f"{row["Tolerance"]}% <br> {row["calc_per"]:.2f} kg" 

            #Change the Format of Deviation column
            if "Deviation" in row and isinstance(row["Deviation"], int):
                value = row["Deviation"]    
                try:
                    row["Deviation"] = Deviation(value).name.capitalize()
                except ValueError:
                    row["Deviation"] =  f"Unknown ({value})"                  
    return data

class DosingType(Enum):
    NORMAL = 1
    LEARNING = 2
    D2E = 100

class Deviation(Enum):
    UNDERDOSING = 1
    NORMAL = 2
    OVERDOSING = 3


