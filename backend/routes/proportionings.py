from flask import Blueprint, jsonify
import psycopg2

# Create the blueprint for the API
bp = Blueprint('proportionings', __name__)

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

# Route to get proportioning data
@bp.route('/api/proportionings', methods=['GET'])
def get_proportionings():
    try:
        # Connect to PostgreSQL database
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

        # Execute the query
        cur.execute(query)
        rows = cur.fetchall()

        # Get column names from the cursor description
        columns = [desc[0] for desc in cur.description]

        # Prepare data by combining rows and column names into a dictionary
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Format the "Actual" field to 4 decimal places if it's a number
            if "Actual" in row_dict and isinstance(row_dict["Actual"], (float, int)):
                row_dict["Actual"] = round(row_dict["Actual"], 4)
            
            data.append(row_dict)

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Return the data as a JSON response
        return jsonify(data)

    except Exception as e:
        # Return an error message if there is an exception
        return jsonify({"error": str(e)})
