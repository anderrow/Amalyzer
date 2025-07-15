# backend/routes/regressor.py
from fastapi import APIRouter, Request
from fastapi import Query
from fastapi.responses import HTMLResponse
from backend.database.config import config
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import LogScatterPlot
from backend.database.query import query_regressor_graph, query_regression_table
from backend.classes.request import RequestLotId, RequestEnvironment
from backend.classes.calculation import CalculateLogTraces
from backend.database.config import *


# Create an APIRouter instance
router = APIRouter(prefix="/regressor")  

@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph(
    request: Request, #Request object to extract the lot_id
    intermediates: int = Query(100), #Parametes for Interemdiate/Bin value (default 200)
    amountOfRegressions: int = Query(2) #Parameter for Amount of Regressions (default 2)    
):
    try:
        db_connection = connect_to_user_environment(request, env_map)
        #Extract lot_id and print it
        lot_id = await RequestLotId(request).return_data() 

        #Format the query with the current lot id
        query = query_regressor_graph.format(current_lot=lot_id)

        #Generate a dataframe with the DB query
        df = await db_connection.fetch_df(query=query) 

        log_traces = CalculateLogTraces(data = df, x_data ="flow", y_data= "opening", 
            size="measurement_time", bins=intermediates, grades=(2,amountOfRegressions+1)) #Regression grade two to Regression Grade (Amount of Regressions+ 1) plot

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

@router.get("/SummaryTable")
async def summary_table(request: Request):
    db_connection = connect_to_user_environment(request, env_map)
    #Extract lot_id
    lot_id = await RequestLotId(request).return_data() 

    data = await fetch_table_data(query_regression_table,db_connection, lot_id)
    
    #Format the query with the current lot id
    query = query_regressor_graph.format(current_lot=lot_id)

    #Generate a dataframe with the DB query (For calculate the length)
    df = await db_connection.fetch_df(query=query) 

    if data:
        data[0]["IntermediateCount"] = f"{len(df)}"
    return data


# ---------- Request data for table  ---------- #
async def fetch_table_data(query_template: str, db_connection: DBConnection, lot_id: int = None) -> dict:
    try:
        #Write the current_prop variable inside the query
        query = query_template.format(current_lot=lot_id)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ------------ Get the current Environment from the request cookies ---------- #
def connect_to_user_environment(request: Request, env_map):
    environment = RequestEnvironment(request).return_data()
    selected_env = env_map.get(environment.upper(), UFA) #Default to UFA if the environment is not found
    return DBConnection(selected_env)