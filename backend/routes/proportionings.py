from fastapi import APIRouter
from fastapi import Query
from backend.classes.db_connection import DBConnection
from backend.classes.filter_data import FilterByString
from typing import List, Dict, Any
from datetime import datetime

# Create an APIRouter instance
router = APIRouter()

#Filter Database to make it more redable
def make_db_redable(data):
    for row in data:
            # Format the "StartTime" field if it's a datetime object
            if "StartTime" in row and isinstance(row["StartTime"], datetime):
                dt = row["StartTime"]
                formatted_start = f"{dt.year}-{dt.strftime('%m')}-{dt.strftime('%d')} {dt.strftime('%A')} {dt.strftime('%H:%M:%S')}"
                row["StartTime"] = formatted_start

            # Format the "EndTime" field if it's a datetime object
            if "EndTime" in row and isinstance(row["EndTime"], datetime):
                dt = row["EndTime"]
                formatted_end = f"{dt.year}-{dt.strftime('%m')}-{dt.strftime('%d')} {dt.strftime('%A')} {dt.strftime('%H:%M:%S')}"
                row["EndTime"] = formatted_end

            # Format the "Actual" field to 4 decimal places if it's a number
            if "Actual" in row and isinstance(row["Actual"], (float, int)):
                row["Actual"] = round(row["Actual"], 4)

    return data

#Filter by func
def filter_by(data, hue):
    filtered_data = []  # List where the filtered rows will be stored

    # Normalize 'hue' to lowercase and strip spaces for a case-insensitive, whitespace-stripped comparison
    normalized_hue = hue.strip().lower()

    for row in data:
        # Check if 'ArticleName' is a string and compare it with normalized 'hue'
        if isinstance(row['ArticleName'], str) and normalized_hue in row['ArticleName'].strip().lower():
            filtered_data.append(row)  # If condition is met, add the row to the list

    return filtered_data

# Database configuration
config = {
    "ConnectionStrings": {
        "DriverName": "PostgreSQL",
        "UserID": "amadeus",
        "Password": "proton",
        "Database": "amadeus",
        "Server": "10.14.4.10",
        "Port": "11008"
    }
}

# Initialize the DBConnection object
db_connection = DBConnection(config=config)

# SQL query to fetch proportioning data
query = """
SELECT 
    amadeus_proportioning.proportioning_dbid AS "ProportioningDBID", 
    amadeus_proportioning.article_dbid AS "ArticleDBID", 
    amadeus_proportioning.lot_dbid AS "LotDBID", 
    amadeus_proportioning.has_vms_data AS "VMSscan", 
    amadeus_article.article_id AS "ArticleID", 
    amadeus_article.name AS "ArticleName", 
    amadeus_lot.lot_id AS "LotID", 
    amadeus_proportioningrecord.requestedamount AS "Requested", 
    amadeus_proportioningrecord.actualamount AS "Actual", 
    amadeus_proportioningrecord.start_time AS "StartTime", 
    amadeus_proportioningrecord.end_time AS "EndTime", 
    amadeus_proportioningrecord.box_id AS "MixBoxID", 
    amadeus_proportioningrecord.ingredientboxid AS "IngBoxID", 
    amadeus_proportioningrecord.proportioninglocation AS "DosingLocation", 
    amadeus_loggingparam.if_in_typeofdosing AS "TypeOfDosing" 
FROM amadeus_proportioning 
JOIN amadeus_proportioningrecord ON amadeus_proportioning.proportioning_dbid = amadeus_proportioningrecord.proportioning_dbid 
JOIN amadeus_loggingparam ON amadeus_proportioning.proportioning_dbid = amadeus_loggingparam.proportioning_dbid 
JOIN amadeus_article ON amadeus_proportioning.article_dbid = amadeus_article.article_dbid 
JOIN amadeus_lot ON amadeus_proportioning.lot_dbid = amadeus_lot.lot_dbid
ORDER BY amadeus_proportioning.proportioning_dbid DESC 
"""


# GET endpoint to retrieve proportioning data
@router.get("/api/proportionings")
async def get_proportionings() -> List[Dict[str, Any]]:
    try:
        # Fetch data from the database
        data = await db_connection.fetch_data(query=query) #Raw Data
        return make_db_redable(data) #Return data after making it redable for the user

    except Exception as e:
        return {"error": str(e)}
    
@router.get("/api/proportioningsfilter")
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

        #Filter by Article if it's requested
        if switchChecked:
            filtered_data = FilterByString(data, requestedArticle, 'ArticleName').apply_filter()
            print("\n"+"*"*30 +"\nArticle Filter Switch enabled")
            print(f"Requested Article: {requestedArticle} \n"+"*"*30+"\n")
            send_filtered_data= True
            
        # Handle Age Filter logic
        if ageSwitchChecked:
            filtered_data = data;# Filter by age range if needed based on rangeValue and timeUnit
            print("\n" + "*" * 30 + "\nAge Filter Switch enabled")
            print(f"Requested Time: {rangeValue} {timeUnit} \n" + "*" * 30 + "\n")
            send_filtered_data= True
            


        if(send_filtered_data): return make_db_redable(filtered_data)
        return make_db_redable(data)
    except Exception as e:
        return {"error": str(e)}  