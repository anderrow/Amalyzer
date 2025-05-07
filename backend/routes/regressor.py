# backend/routes/regressor.py
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sklearn.linear_model import LinearRegression
from backend.database.config import config
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import TraceData, LogScatterPlot
from backend.database.query import query_regressor_graph
from backend.classes.request import RequestLotId, RequestPropId
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
        print("\n" + "*"*37 + f"\n* LotID: {lot_id} from proportioning {RequestPropId().return_data()} *\n" + "*"*37)

        #Format the query with the current lot id
        query = query_regressor_graph.format(current_lot=lot_id)
        #Generate a dataframe with the DB query
        df = await db_connection.fetch_df(query=query)

        # Regressions
        df['log_flow'] = np.log10(df['flow'])

        x_range = np.linspace(df['log_flow'].min(), df['log_flow'].max(), 200)
        flow_range = 10 ** x_range

        reg = LinearRegression().fit(df['log_flow'].values.reshape(-1, 1), df['opening'])
        
        y_linear = reg.predict(x_range.reshape(-1, 1))

        coefs_deg2 = np.polyfit(df['log_flow'], df['opening'], 2)
        y_deg2 = np.polyval(coefs_deg2, x_range)

        coefs_deg3 = np.polyfit(df['log_flow'], df['opening'], 3)
        y_deg3 = np.polyval(coefs_deg3, x_range)

        #Generate an empty list for traces
        trace_list = []
        #Generate TraceData object and append it
        trace_list.append(TraceData(label="Intermediates", x_data=df['flow'],  y_data=df['opening'], mode="markers", color="blue", marker=dict(size=df['measurement_time'] *3 , color='blue', opacity=0.7))) #Raw Data
        trace_list.append(TraceData(label="Linear Regression", x_data=flow_range,  y_data=y_linear, mode="lines", color="grey", dash="dash")) #Linear Regression
        trace_list.append(TraceData(label="Polynomial Degree 2", x_data=flow_range,  y_data=y_deg2, mode="lines", color="red", dash="dash")) #2nd Grade
        trace_list.append(TraceData(label="Polynomial Degree 3", x_data=flow_range,  y_data=y_deg3, mode="lines", color="lime", dash="dash")) #3rd Grade
        
        graph_html = LogScatterPlot(
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


