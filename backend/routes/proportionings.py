from fastapi import APIRouter
from .db_connection import DBConnection # Import the DBConnection class
from typing import List, Dict, Any
from datetime import datetime

# Create an APIRouter instance
router = APIRouter()

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
        data = await db_connection.fetch_data(query=query)

        # Format the "StartTime" field if it's a datetime object
        for row in data:
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

    except Exception as e:
        return {"error": str(e)}
