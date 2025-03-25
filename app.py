from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)  # Permite peticiones desde el frontend

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

# Ruta para obtener los datos
@app.route('/api/proportionings', methods=['GET'])
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
        data = [dict(zip(columns, row)) for row in rows]

        cur.close()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

# Ejecutar el servidor
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
