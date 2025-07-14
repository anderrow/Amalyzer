from fastapi import APIRouter
from fastapi import Query
from backend.database.config import config
from backend.database.query import query_proportionings, query_proportionings_filter
from backend.classes.db_connection import DBConnection
from backend.classes.filter_data import  ReadableDataFormatter, FilterByString, Deviation
from backend.classes.request import PropIdRequest
from backend.classes.calculation import CaclulateDateDelta, CaclulatPercent, IsInTolerance, NumericDeviation
from backend.memory.state import session_data
from typing import List, Dict, Any
import pandas as pd
from pydantic import BaseModel

class PropIdRequest(BaseModel):
    propDbId: int   # Include propDbId in the request model for tracking purposes
    uid: str  # Include UID in the request model for tracking purposes

# Create an APIRouter instance
router = APIRouter()

# Initialize the DBConnection object
db_connection = DBConnection(config) #config is declared in backend/database/config.py

# ----------------- GET endpoint to retrieve proportioning data (Controls -> Update button) ----------------- #

@router.get("/api/proportionings")
async def get_proportionings() -> List[Dict[str, Any]]:
    try:

        # Fetch data from the database
        data = await db_connection.fetch_df(query_proportionings) #Raw Data (Limited to 1000 rows by default)

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
    rangeValue: int = Query(50),  # Parameter for slider value (default to 50) 
    deviationSwitchChecked: bool = Query(False),  # Parameter for Deviation Filter switch (Default False)
    requestedDeviation: str = Query("")  # Parameter for requested deviation type (Default is empty string, if no input is given) 
) -> List[Dict[str, Any]]:
    
    try:
        # Copy the base query for proportionings
        query_proportionings_filtered = query_proportionings_filter

        # Initialize an empty where clause (To avoid errors if no filters are applied with "none" values in the query)
        where_clause = ""

        # Initialize an empty list to hold conditions
        conditions = []
        #Filter by Article if it's requested
        if switchChecked:
            conditions.append(f"name = '{requestedArticle}'")  # Add condition for ArticleName
            print("\n"+"*"*50 +"\n* Article Filter Switch enabled" + " "*18 + "*")
            print(f"* Requested Article: {requestedArticle:<28}* \n"+"*"*50+"\n")
            
            
        # Handle Age Filter logic
        if ageSwitchChecked:
            # Filter by age range if needed based on rangeValue and timeUnit
            conditions.append(f"start_time >= NOW() - INTERVAL '{rangeValue} {timeUnit}'")
            # Add the age filter to the where clause
            print("\n" + "*" * 50 + "\n* Age Filter Switch enabled" + " "*22 + "*")
            print(f"* Requested Time: {rangeValue} {timeUnit:<28}* \n" + "*" * 50 + "\n")

        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Fetch data from the database
        data = await db_connection.fetch_df(query=query_proportionings_filtered.format(where_clause=where_clause)) #Raw Data
            
        data = calculate(data)

        # If deviation switch is checked, filter by requested deviation type (This is done in the backend, that's why is done after fetching the data)
        if deviationSwitchChecked:
            print("\n"+"*"*50 +"\n* Deviation Filter Switch enabled" + " "*16 + "*")
            print(f"* Requested Deviation Type: {Deviation(int(requestedDeviation)).name:<21}* \n"+"*"*50+"\n") #print the requested deviation type name, not the numeric value.
            data = FilterByString(data, requestedDeviation, "Deviation").apply_filter() 

        #Make all the calculations that are needed (After filtering the data for avoiding unnecessary calculations)
        if not data.empty:
            data = data.head(500).copy()  # Limit to 500 rows for performance reasons
            #Make data redable
            data = make_db_redable(data)

        return data
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}  


# ----------------- Define a POST route that listens for row click events from the frontend ----------------- #
@router.post("/api/rowclicked")
async def handle_row_click( body: PropIdRequest):
    # Extract the UID and propDbId from the request body
    uid = body.uid
    propDbId = body.propDbId

    # Print the UID from the request cookies to the backend console for debugging/logging purposes
    print("\n"+"*"*50+ "\n" + f"* UID:{uid:<43}*")
    # Print the received propDbId to the backend console for debugging/logging purposes
    print("*"*50+ "\n" + f"* PropDBID selected: {propDbId:<28}*"+ "\n" + "*"*50 + "\n")
    # Check if the session_data dictionary already has an entry for the UID
    # If not, create a new entry for the UID
    if uid not in session_data:
        session_data[uid] = {}

    session_data[uid]["current_prop_id"] = propDbId # Store the propDbId in the session_data dictionary under the UID

    return {"propDbId": body.propDbId} # Return a confirmation message as a JSON response (Not mandatory for now)

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
    #Add Numeric Deviation column
    data = NumericDeviation(data, "Requested", "Actual").apply_calculation()

    return data
#  -----------------  Filter Database to make it more redable  ----------------- #
def make_db_redable(df: pd.DataFrame) -> List[Dict[str, Any]]:
    formatter = ReadableDataFormatter(df)
    return formatter.apply_all_formats()


