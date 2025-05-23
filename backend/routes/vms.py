# backend/routes/vms.py
from fastapi import APIRouter
from fastapi import Query
from fastapi.responses import HTMLResponse
from backend.database.config import config_UFA_PROD
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import Traces3DPlot , TraceData
from backend.database.query import query_vms_data
import numpy as np
import pandas as pd

# Create an APIRouter instance
router = APIRouter(prefix="/vms")  
# Initialize the DBConnection object
db_connection = DBConnection(config=config_UFA_PROD) 

# Example endpoint to check vms status
@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph():
    try:

        #Format the query with the current proportioning id
        #query = query_vms_data.format(current_lot=lot_id)
        query = query_vms_data

        #Generate a dataframe with the DB query
        df = await db_connection.fetch_df(query=query) 

        #Filter the datafram here
        df = take_data_inside_the_box(df)

        #Extra information
        n = len(df) #Samples
        y_vals = np.linspace(0, 570, n) #Space then equally in 570 values

        #Generate an empty list for traces
        trace_list = []
        #Generate TraceData object and append it
        trace_list.append(TraceData("z0", x_data=np.zeros(n), y_data=y_vals, z_data=np.full(n, 900), color="white"))
        trace_list.append(TraceData("Left", x_data=np.zeros(n), y_data=y_vals, z_data=df["sensor_l"], color="black"))
        trace_list.append(TraceData("Middle", x_data=np.full(n, 180), y_data=y_vals, z_data=df["sensor_m"], color="red"))
        trace_list.append(TraceData("Right", x_data=np.full(n, 360), y_data=y_vals, z_data=df["sensor_r"], color="blue"))
        trace_list.append(TraceData("z1", x_data=np.full(n, 360), y_data=y_vals,  z_data= np.full(n, 900), color="white"))

        graph_html = Traces3DPlot(trace_list).plot_graph()

        # Return raw HTML
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Retrun error
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)
    
# ------------- Taking only the VMS data inside the box ------------- #

# Function to trim the dataframe and keep only the part inside the "box"
def take_data_inside_the_box(df):
    # Detect the start index of the hill in the sensor_m data
    start = detect_hill_start(df["sensor_m"].to_numpy())
    # Detect the end index of the hill in the sensor_m data
    end = detect_hill_end(df["sensor_m"].to_numpy())
    # Slice the dataframe from start to end and reset the index
    trimmed_df = df.iloc[start:end].reset_index(drop=True)

    return trimmed_df

# Function to detect the start of a hill in a numeric series
def detect_hill_start(series, rise_thresh=50, plateau_margin=5, plateau_points=10):
    # Calculate the difference between consecutive points in the series
    diffs = np.diff(series)

    # Iterate over differences to find where the slope rises above threshold
    for i in range(len(diffs) - plateau_points):
        if diffs[i] > rise_thresh:
            # Check if the next points form a relatively flat plateau
            window = series[i+1:i+1+plateau_points]
            if np.all(np.abs(np.diff(window)) < plateau_margin):
                # Return the index right after the rise starts
                return i + 1
    # If no hill start found, return 0 (start of series)
    return 0

# Function to detect the end of a hill in a numeric series
def detect_hill_end(series, fall_thresh=-50, plateau_margin=5, plateau_points=10):
    # Calculate the difference between consecutive points in the series
    diffs = np.diff(series)

    # Iterate backward over differences to find where slope falls below threshold
    for i in range(len(diffs) - 1, plateau_points, -1):
        if diffs[i-1] < fall_thresh:
            # Check if the previous points form a relatively flat plateau
            window = series[i-plateau_points:i]
            if np.all(np.abs(np.diff(window)) < plateau_margin):
                # Return the index where the fall ends
                return i
    # If no hill end found, return length of series (end of data)
    return len(series)
