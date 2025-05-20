# backend/routes/regressor.py
from fastapi import APIRouter
from fastapi import Query
from fastapi.responses import HTMLResponse
from backend.memory.state import session_data
from backend.database.config import config
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import LogScatterPlot
from backend.database.query import query_regressor_graph, query_regression_table
from backend.classes.request import RequestLotId, RequestPropId
from backend.classes.calculation import CalculateLogTraces


# Create an APIRouter instance
router = APIRouter(prefix="/regressor")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph(
    intermediates: int = Query(100), #Parametes for Interemdiate/Bin value (default 200)
    amountOfRegressions: int = Query(2) #Parameter for Amount of Regressions (default 2)
):
    try:
        #Extract lot_id and print it
        lot_id = await RequestLotId().return_data() 
        debug(lot_id) #Print in console

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
async def summary_table():
    data = await fetch_table_data(query_regression_table)

    #Extract lot_id and print it
    lot_id = await RequestLotId().return_data() 
    #Format the query with the current lot id
    query = query_regressor_graph.format(current_lot=lot_id)
    #Generate a dataframe with the DB query (For calculate the length)
    df = await db_connection.fetch_df(query=query) 

    if data:
        data[0]["IntermediateCount"] = f"{len(df)}"
    return data

# ---------- Debug by console   ---------- #
def debug(lot_id):
    print( # Debugging by console
        "\n" + "*" * 40 +
        f"\n* LotID: {f'{lot_id}':<30}*" +
        f"\n* ProportioningID: {f': {RequestPropId().return_data()}':<20}*" +
        "\n" + "*" * 40 + "\n")
    
# ---------- Request data for table  ---------- #
async def fetch_table_data(query_template: str):
    try:
        #Get current lot id
        lot_id = await RequestLotId().return_data() 
        #Write the current_prop variable inside the query
        query = query_template.format(current_lot=lot_id)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}