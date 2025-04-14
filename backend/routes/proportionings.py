from fastapi import APIRouter
import psycopg2
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

# GET endpoint to retrieve proportioning data
@router.get("/api/proportionings")
def get_proportionings():
    try:
        # Connect to the PostgreSQL database using the configuration parameters
        conn = psycopg2.connect(
            dbname=config['ConnectionStrings']['Database'],
            user=config['ConnectionStrings']['UserID'],
            password=config['ConnectionStrings']['Password'],
            host=config['ConnectionStrings']['Server'],
            port=config['ConnectionStrings']['Port']
        )
        cur = conn.cursor()

        # SQL query to fetch proportioning data from multiple tables
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

        # Execute the SQL query
        cur.execute(query)
        rows = cur.fetchall()

        # Retrieve column names from the cursor description
        columns = [desc[0] for desc in cur.description]

        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Format the "StartTime" field if it's a datetime object
            if "StartTime" in row_dict and isinstance(row_dict["StartTime"], datetime):
                dt = row_dict["StartTime"]
                # Format date with zero-padded month and day; day name with first letter uppercase
                formatted_start = f"{dt.year}-{dt.strftime('%m')}-{dt.strftime('%d')} {dt.strftime('%A')} {dt.strftime('%H:%M:%S')}"
                row_dict["StartTime"] = formatted_start
            
            # Format the "EndTime" field if it's a datetime object
            if "EndTime" in row_dict and isinstance(row_dict["EndTime"], datetime):
                dt = row_dict["EndTime"]
                formatted_end = f"{dt.year}-{dt.strftime('%m')}-{dt.strftime('%d')} {dt.strftime('%A')} {dt.strftime('%H:%M:%S')}"
                row_dict["EndTime"] = formatted_end

            # Format the "Actual" field to 4 decimal places if it's a number
            if "Actual" in row_dict and isinstance(row_dict["Actual"], (float, int)):
                row_dict["Actual"] = round(row_dict["Actual"], 4)
            
            data.append(row_dict)

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Return the data as JSON; FastAPI automatically converts the return to JSON
        return data

    except Exception as e:
        # Return an error message if an exception occurs
        return {"error": str(e)}

