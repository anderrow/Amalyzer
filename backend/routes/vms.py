# backend/routes/vms.py
import numpy as np
from fastapi import APIRouter, Request
from fastapi import Query
from fastapi.responses import HTMLResponse
from backend.database.config import config
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import Traces3DPlot , TraceData
from backend.classes.request import RequestPropId, RequestEnvironment
from backend.database.query import query_vms_data
from backend.database.config import *

# Create an APIRouter instance
router = APIRouter(prefix="/vms")  

# Example endpoint to check vms status
@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph(request: Request):
    try:
        db_connection = connect_to_user_environment(request, env_map)

        current_prop = RequestPropId(request).return_data()
        #Take the data from the prop ID requested
        df = await db_connection.fetch_df(query_vms_data, current_prop)

        #Filter the dataframe to only take the data INSIDE the box 
        #df = take_data_inside_the_box(df)
        df = df[(df["sensor_m"] < 625) & (df["sensor_m"] > 350)]
        df = df[(df["sensor_l"] < 625) & (df["sensor_l"] > 350)]
        df = df[(df["sensor_r"] < 625) & (df["sensor_r"] > 350)]
        #Extra information
        n = len(df) #Number of Samples
        y_vals = np.linspace(0, 570, n) #Space then equally in 570 values (Distance of the box)

        #Load x values for each sensor (Needs to be taken from db, also the height of the sensors)
        x_left=18
        x_mid=160
        x_right=340

        #Iterate new values for the material on the wall of the box
        m_left = (df["sensor_m"]-df["sensor_l"])/(x_mid-x_left)
        z_left_zero = m_left * (0- x_left) + df["sensor_l"]

        m_right = (df["sensor_m"]-df["sensor_r"])/(x_mid-x_right)
        z_right_zero = m_right * (367 - x_right) + df["sensor_r"]
        
        #Generate an empty list for traces
        trace_list = []
        #Generate TraceData object and append it
        trace_list.append(TraceData("z0", x_data=np.zeros(n), y_data=y_vals, z_data=np.full(n, 650), color="grey", dash='dot'))
        trace_list.append(TraceData("LeftZero", x_data=np.zeros(n), y_data=y_vals, z_data=z_left_zero, color="black", dash='dot'))
        trace_list.append(TraceData("Left", x_data=np.full(n, x_left), y_data=y_vals, z_data=df["sensor_l"], color="black"))
        trace_list.append(TraceData("Middle", x_data=np.full(n, x_mid), y_data=y_vals, z_data=df["sensor_m"], color="red"))
        trace_list.append(TraceData("Right", x_data=np.full(n, x_right), y_data=y_vals, z_data=df["sensor_r"], color="blue"))
        trace_list.append(TraceData("RightZero", x_data=np.full(n, 367), y_data=y_vals, z_data=z_right_zero, color="blue", dash='dot'))
        trace_list.append(TraceData("z1", x_data=np.full(n, 367), y_data=y_vals,  z_data= np.full(n, 650), color="gray", dash='dot'))

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

# ------------ Get the current Environment from the request cookies ---------- #
def connect_to_user_environment(request: Request, env_map):
    environment = RequestEnvironment(request).return_data()
    selected_env = env_map.get(environment.upper(), UFA) #Default to UFA if the environment is not found
    return DBConnection(selected_env)