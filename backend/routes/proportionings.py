from flask import Blueprint, jsonify
import psycopg2

# Crear el blueprint
bp = Blueprint('proportionings', __name__)

# Configuración de la base de datos
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

@bp.route('/api/proportionings', methods=['GET'])
def get_proportionings():
    try:
        # Conexión a PostgreSQL
        conn = psycopg2.connect(
            dbname=config['ConnectionStrings']['Database'],
            user=config['ConnectionStrings']['UserID'],
            password=config['ConnectionStrings']['Password'],
            host=config['ConnectionStrings']['Server'],
            port=config['ConnectionStrings']['Port']
        )
        cur = conn.cursor()

        # Query
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

        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            
            # Format "Actual" to 4 decimal places if it exists and is a number
            if "Actual" in row_dict and isinstance(row_dict["Actual"], (float, int)):
                row_dict["Actual"] = round(row_dict["Actual"], 4)
            
            data.append(row_dict)

        cur.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})