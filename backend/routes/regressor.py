# backend/routes/regressor.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sklearn.linear_model import LinearRegression
from backend.database.config import config
from backend.memory.state import session_data
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import TraceData, LogScatterPlot
from backend.database.query import query_regressor_graph, query_lot_db_id
import numpy as np



# Create an APIRouter instance
router = APIRouter(prefix="/regressor")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

# Example endpoint to check regressor status
@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_lot_db_id.format(current_prop=current_prop)
        #Save lot_id
        lot_id = await db_connection.fetch_data(query=query)
        #Extract the lot_id from the Json
        lot_id = lot_id[0]["lot_dbid"] 

        print("\n" + "*"*50 + f"LotID: {lot_id} from proportioning {current_prop}* \n" + "*"*50) #Debug
        query = query_regressor_graph.format(current_lot=lot_id)

        df = await db_connection.fetch_df(query=query)

        #Generate an empty list for traces
        trace_list = []

        df['log_flow'] = np.log10(df['flow'])

        # Regressions
        x_range = np.linspace(df['log_flow'].min(), df['log_flow'].max(), 200)
        flow_range = 10 ** x_range

        reg = LinearRegression().fit(df['log_flow'].values.reshape(-1, 1), df['opening'])
        
        y_linear = reg.predict(x_range.reshape(-1, 1))

        coefs_deg2 = np.polyfit(df['log_flow'], df['opening'], 2)
        y_deg2 = np.polyval(coefs_deg2, x_range)

        coefs_deg3 = np.polyfit(df['log_flow'], df['opening'], 3)
        y_deg3 = np.polyval(coefs_deg3, x_range)

        #Generate TraceData object and append it
        trace_list.append(TraceData(label="Intermediates", x_data=df['flow'],  y_data=df['opening'], mode="markers", color="blue", marker=dict(size=df['measurement_time'] *3 , color='blue', opacity=0.7))) #Raw Data
        trace_list.append(TraceData(label="Linear Regression", x_data=flow_range,  y_data=y_linear, mode="lines", color="grey", dash="dash")) #Linear Regression
        trace_list.append(TraceData(label="Polynomial Degree 2", x_data=flow_range,  y_data=y_deg2, mode="lines", color="red", dash="dash")) #2nd Grade
        trace_list.append(TraceData(label="Polynomial Degree 3", x_data=flow_range,  y_data=y_deg3, mode="lines", color="lime", dash="dash")) #3rd Grade
        
        graph_html = LogScatterPlot(
            session_data.get("current_prop_id"), 
            title="", 
            xaxis_title="Flow[kg/s]", 
            yaxis_title="Slide position [mm]", 
            traces=trace_list,
            leyend_pos=["top", "left"]
        ).plot_graph()

        # Return raw HTML
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Retrun error
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)
    