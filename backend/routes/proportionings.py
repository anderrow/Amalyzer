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
        data = await db_connection.fetch_df(query=query_proportionings) #Raw Data

        #Make all the calculations that are needed
        data = calculate(data)

        #Make data redable
        data = make_db_redable(data)

        return data #Return data

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
        data = await db_connection.fetch_df(query=query_proportionings)

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
        
        #Make data redable
        data = make_db_redable(data)

        return data
        
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
    if data is None:
        print("Data Is None")
    return data
#  -----------------  Filter Database to make it more redable  ----------------- #
def make_db_redable(df: pd.DataFrame) -> List[Dict[str, Any]]:
    # Format "StartTime"
    if "StartTime" in df.columns:
        df["StartTime"] = pd.to_datetime(df["StartTime"], errors="coerce")
        df["StartTime"] = df["StartTime"].dt.strftime("%Y-%m-%d %A %H:%M:%S")

    # Format "Actual" to 4 decimal places
    if "Actual" in df.columns:
        df["Actual"] = pd.to_numeric(df["Actual"], errors="coerce").round(4)

    # Convert boolean "VMSscan" to emojis
    if "VMSscan" in df.columns:
        df["VMSscan"] = df["VMSscan"].map({True: "✅", False: "❌"})

    # Format "LotID"
    if "LotID" in df.columns:
        df["LotID"] = df["LotID"].astype(str).str.replace("##", "#<br>#", regex=False)

    # Format "TypeOfDosing" using Enum
    if "TypeOfDosing" in df.columns:
        def format_dosing(val):
            try:
                return DosingType(val).name.capitalize()
            except ValueError:
                return f"Unknown ({val})"
        df["TypeOfDosing"] = df["TypeOfDosing"].apply(format_dosing)

    # Format "Tolerance" with percentage and weight (calc_per must exist)
    if "Tolerance" in df.columns and "calc_per" in df.columns:
        def format_tolerance(row):
            try:
                tol = float(row["Tolerance"])
                kg = float(row["calc_per"])
                return f"{tol}% <br> {kg:.2f} kg"
            except:
                return row["Tolerance"]
        df["Tolerance"] = df.apply(format_tolerance, axis=1)

    # Format "Deviation" using Enum
    if "Deviation" in df.columns:
        def format_deviation(val):
            try:
                return Deviation(val).name.capitalize()
            except ValueError:
                return f"Unknown ({val})"
        df["Deviation"] = df["Deviation"].apply(format_deviation)

    # Return as list of dicts for FastAPI response
    return df.to_dict(orient="records")

class DosingType(Enum):
    NORMAL = 1
    LEARNING = 2
    D2E = 100

class Deviation(Enum):
    OVERDOSING = 1
    NORMAL = 2
    UNDERDOSING = 3


