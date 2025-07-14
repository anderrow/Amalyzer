from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import PlotPointsinTime, TraceData
from backend.database.config import config
from backend.classes.request import RequestPropId
from backend.classes.calculation import CaclulateDateDelta, CaclulatPercent , IsInTolerance , NumericDeviation
from backend.classes.filter_data import Deviation , DosingType
from backend.database.query import query_analyzer_summary, query_analyzer_propRecord, query_analyzer_logginParam, query_analyzer_lot, query_analyzer_article, query_analyzer_slide_graph, query_analyzer_flow, query_analyzer_dosed_material


router = APIRouter(prefix="/analyzer")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py   

# ---------- Generate and return interactive graph SLIDE POSITION  ---------- #
@router.get("/Graph1", response_class=HTMLResponse)
async def generate_graph(request: Request):
    try:
        current_prop = get_current_prop_id(request) # Get the current proportioning ID from the request cookies

        df = await db_connection.fetch_df(query=query_analyzer_slide_graph, current_prop=current_prop)

        debug(current_prop, "Slide Position") # Debugging by console

        #Generate an empty list for traces
        trace_list = []
        #Generate TraceData object and append it
        trace_list.append(TraceData(label="Vibratos",  sample_time=0.01, x_data=df.index,  y_data=[5 if y else -10 for y in df["dc_out_controlvibrator"]], mode="markers", color="grey"))
        trace_list.append(TraceData(label="Knocer",  sample_time=0.01, x_data=df.index,  y_data=[2.5 if y else -10 for y in df["dc_out_controlknocker"]], mode="markers", color="purple"))
        trace_list.append(TraceData(label="Desired Position",  sample_time=0.01, x_data=df.index,  y_data=df["dc_out_desiredslideposition"], mode="lines", color="pink"))
        trace_list.append(TraceData(label="Real Time Position",  sample_time=0.01, x_data=df.index,  y_data=df["plant_out_slideposition"], mode="lines", color="blue"))

        
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
    

# ---------- Generate and return interactive graph  DOSED MATERIAL---------- #
@router.get("/Graph2", response_class=HTMLResponse)
async def generate_graph(request: Request):
    try:
        current_prop = get_current_prop_id(request) # Get the current proportioning ID from the request cookies

        debug(current_prop,"Dosed Material") # Debugging by console

        df = await db_connection.fetch_df(query=query_analyzer_dosed_material, current_prop=current_prop)

        summary = await db_connection.fetch_df(query_analyzer_summary, current_prop=current_prop)

        requested = float(summary["Requested"].iloc[0])
        tolerance = float(summary["Tolerance"].iloc[0]) / 100
        upper_tolerance = requested * (1 + tolerance)
        lower_tolerance = requested * (1 - tolerance)


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

# ---------- Generate and return interactive graph SLIDE POSITION  ---------- #
@router.get("/Graph3", response_class=HTMLResponse)
async def generate_graph(request: Request):
    try:
        current_prop = get_current_prop_id(request) # Get the current proportioning ID from the request cookies

        df = await db_connection.fetch_df(query=query_analyzer_flow, current_prop=current_prop)
        debug(current_prop, "Material Flow") # Debugging by console

        #Generate an empty list for traces
        trace_list = []
        #Generate TraceData object and append it
        trace_list.append(TraceData(label="Expected Flow",  sample_time=0.01, x_data=df.index,  y_data=df["dc_out_expectedflow"], mode="lines", color="blue"))
        trace_list.append(TraceData(label="Desired Flow",  sample_time=0.01, x_data=df.index,  y_data=df["dc_out_desiredflow"], mode="lines", color="pink",  dash="dash"))
        trace_list.append(TraceData(label="Actual Flow",  sample_time=0.01, x_data=df.index,  y_data=df["f_out_filteredflow2"], mode="lines", color="green"))
        
        graph_html = PlotPointsinTime( 
            title="Material Flow", 
            xaxis_title="Seconds", 
            yaxis_title="Kg/s", 
            traces=trace_list,
            leyend_pos=["top", "right"]
        ).plot_graph()

        # Return raw HTML
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Aquí podrías devolver un HTML de error, o un JSON si prefieres
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)
    

# ---------- SUMMARY TABLE ---------- #
@router.get("/Summary")
async def summary_table(request: Request):
    data = await db_connection.fetch_df(query_analyzer_summary, get_current_prop_id(request))
    
    data = calculate(data) #Make all the calculations that are needed
    
    data = data.rename(columns={"ArticleName": "Article Name",
                                "LotID": "Lot ID",
                                "LotDBID": "Lot DB ID",
                                "calc_per": "Tolerance (Kg)",
                                "Tolerance": "Tolerance %",
                                "Actual": "Actual (Kg)",
                                "Requested": "Requested (Kg)",
                                "NumericDeviation": "Numeric Deviation (Kg)",
                                "NumericDeviationPercent": "Numeric Deviation %",})
    
    data["Deviation"] = data["Deviation"].apply(lambda val: Deviation(val).name.capitalize()) # for val in data["Deviation"] -> Deviation(val).name.capitalize()
    data["Type Of Dosing"] = data["Type Of Dosing"].apply(lambda val: DosingType(val).name.capitalize() if val else "Unknown") # for val in data["TypeOfDosing"] -> DosingType(val).name.capitalize()

    return data.to_dict(orient="records") #FastAPI expects a list of dictionaries for JSON response

# ---------- PROP RECORD ---------- #    
@router.get("/PropRecord")
async def propRecord_table(request: Request):
    data = await db_connection.fetch_df(query_analyzer_propRecord, get_current_prop_id(request))
    return data.to_dict(orient="records") 

# ---------- Logging Param ---------- #    
@router.get("/LogginParam")
async def propRecord_table(request: Request):
    data = await db_connection.fetch_df (query_analyzer_logginParam, get_current_prop_id(request))
    return data.to_dict(orient="records") 

# ---------- Lot table ---------- #    
@router.get("/Lot")
async def lot_table(request: Request):
    data = await db_connection.fetch_df(query_analyzer_lot, get_current_prop_id(request))
    return data.to_dict(orient="records") 

# ---------- Article table ---------- #    
@router.get("/Article")
async def article_table(request: Request):
    data = await db_connection.fetch_df(query_analyzer_article, get_current_prop_id(request))
    return data.to_dict(orient="records") 




# ------------ Get the current proportioning ID from the request cookies ---------- #
def get_current_prop_id(request: Request):
    current_prop = RequestPropId(request).return_data()
    return current_prop

# ---------- Debugging by console  ---------- #
def debug(prop_id,num):
    print( # Debugging by console
        "\n" + "*" * 52 +
        f"\n* Plotting Graph {num} for PropID: {f': {prop_id}':<7}*" +
        "\n" + "*" * 52 + "\n" )   

# ----------------- Make all the calculations that are needed ----------------- #
def calculate(data):
    #Overwrite Endtime with EndTime - StartTime to calculate duration
    data = CaclulateDateDelta(data, "Dosing Date", "Duration", overwrite=True).apply_calculation()
    #Add percentage calculation column
    data = CaclulatPercent(data, "Requested", "Tolerance", overwrite=False).apply_calculation()
    #Add deviation column
    data = IsInTolerance(data, "Requested", "Actual", "Tolerance").apply_calculation()
    #Add Numeric Deviation column
    data = NumericDeviation(data, "Requested", "Actual").apply_calculation()

    return data