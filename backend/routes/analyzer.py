from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from backend.memory.state import session_data
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import PlotPointsinTime, TraceData
from backend.database.config import config
from backend.classes.request import RequestPropId
from backend.database.query import query_analyzer_summary, query_analyzer_propRecord, query_analyzer_logginParam, query_analyzer_lot, query_analyzer_article, query_analyzer_slide_graph
router = APIRouter(prefix="/analyzer")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py   

# ---------- Generate and return interactive graph ---------- #
@router.get("/Graph1", response_class=HTMLResponse)
async def generate_graph():
    try:
        df = await db_connection.fetch_df(query=query_analyzer_slide_graph)

        #Generate an empty list for traces
        trace_list = []
        #Generate TraceData object and append it
        trace_list.append(TraceData(label="Desired Position",  sample_time=0.01, x_data=df.index,  y_data=df["dc_out_desiredslideposition"], mode="lines", color="pink"))
        trace_list.append(TraceData(label="Real Time Position",  sample_time=0.01, x_data=df.index,  y_data=df["plant_out_slideposition"], mode="lines", color="blue"))
        trace_list.append(TraceData(label="Vibratos",  sample_time=0.01, x_data=df.index,  y_data=[5 if y else -10 for y in df["dc_out_controlvibrator"]], mode="markers", color="grey"))
        trace_list.append(TraceData(label="Knocer",  sample_time=0.01, x_data=df.index,  y_data=[2.5 if y else -10 for y in df["dc_out_controlknocker"]], mode="markers", color="purple"))
        
        graph_html = PlotPointsinTime( 
            title="Slide Position", 
            xaxis_title="Seconds", 
            yaxis_title="mm", 
            traces=trace_list,
            leyend_pos=["top", "right"]
        ).plot_graph()

        # Return raw HTML
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Aquí podrías devolver un HTML de error, o un JSON si prefieres
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)
    
# ---------- Generate and return interactive graph ---------- #
@router.get("/Graph2", response_class=HTMLResponse)
async def generate_graph():
    try:
        df = await db_connection.fetch_df(query=query_analyzer_slide_graph)
        summary = await fetch_table_data(query_analyzer_summary)
        requested = float(summary[0]['Requested'])
        tolerance = float(summary[0]['Requested'])/100
        upper_tolerance = requested *  (1+tolerance)
        lower_tolerance = requested * (1-tolerance)

        trace_list = []
        #Smoothed filter for erasing small variations
        df['Smoothed'] = df["if_out_dosedweight"].rolling(window=100).mean().fillna(0) #0.1 seconds

        #Generate TraceData object
        trace_list.append(TraceData(label="Smoothed Dosed Material",  sample_time=0.01, x_data=df.index,  y_data=df["Smoothed"], mode="lines", color="grey")) 
        trace_list.append(TraceData(label="Dosed Material",  sample_time=0.01, x_data=df.index,  y_data=df["if_out_dosedweight"], mode="lines", color="red"))
        trace_list.append(TraceData(label="Set Point",  sample_time=0.01, x_data=df.index,  y_data=[requested] * len(df.index), mode="lines", color="Blue")) #Setpoint
        trace_list.append(TraceData(label="Upper Tolerance",  sample_time=0.01, x_data=df.index,  y_data=[upper_tolerance] * len(df.index), mode="lines", color="Green", dash="dash"))
        trace_list.append(TraceData(label="Lower Tolerance",  sample_time=0.01, x_data=df.index,  y_data=[lower_tolerance] * len(df.index), mode="lines", color="Green", dash="dash"))

        graph_html = PlotPointsinTime(
            title="Dosed Material", 
            xaxis_title="Seconds", 
            yaxis_title="kg", 
           traces=trace_list,
           leyend_pos=["bottom", "right"]
        ).plot_graph()

        # Return raw HTML
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Aquí podrías devolver un HTML de error, o un JSON si prefieres
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)

# ---------- Get Actual PropId to analyze ---------- #
@router.get("/PropId")
async def analyzer_status():
    current_prop = RequestPropId().return_data()
    return current_prop

# ---------- SUMMARY TABLE ---------- #
@router.get("/Summary")
async def summary_table():
    return await fetch_table_data(query_analyzer_summary)

# ---------- PROP RECORD ---------- #    
@router.get("/PropRecord")
async def propRecord_table():
    return await fetch_table_data(query_analyzer_propRecord)
    

# ---------- Logging Param ---------- #    
@router.get("/LogginParam")
async def propRecord_table():
    return await fetch_table_data(query_analyzer_logginParam)
    

# ---------- Logging Param ---------- #    
@router.get("/Lot")
async def lot_table():
    return await fetch_table_data(query_analyzer_lot)
    
# ---------- Logging Param ---------- #    
@router.get("/Article")
async def article_table():
    return await fetch_table_data(query_analyzer_article)



# ---------- Request data for table  ---------- #
async def fetch_table_data(query_template: str):
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_template.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    