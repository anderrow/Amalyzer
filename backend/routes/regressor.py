# backend/routes/regressor.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sklearn.linear_model import LinearRegression
from backend.database.config import config
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import TraceData, LogScatterPlot
from backend.database.query import query_regressor_graph
from backend.classes.request import RequestLotId, RequestPropId
from backend.classes.calculation import CalculateLogTraces
import numpy as np

# Create an APIRouter instance
router = APIRouter(prefix="/regressor")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph():
    try:
        #Extract lot_id and print it
        lot_id = await RequestLotId().return_data()
        
        print( # Debugging by console
        "\n" + "*" * 40 +
        f"\n* LotID: {f'{lot_id}':<30}*" +
        f"\n* ProportioningID: {f': {RequestPropId().return_data()}':<20}*" +
        "\n" + "*" * 40)

        #Format the query with the current lot id
        query = query_regressor_graph.format(current_lot=lot_id)

        #Generate a dataframe with the DB query
        df = await db_connection.fetch_df(query=query) 

        log_traces = CalculateLogTraces(data = df, x_data ="flow", y_data= "opening",
            size="measurement_time", bins=200, grades=(1,10))

        graph_html = LogScatterPlot(
            title="", 
            xaxis_title="Flow[kg/s]", 
            yaxis_title="Slide position [mm]", 
            traces=log_traces.apply_calculation(),
            leyend_pos=["top", "left"]
        ).plot_graph()

        # Return raw HTML
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Retrun error
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)


