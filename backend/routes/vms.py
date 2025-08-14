# backend/routes/vms.py
import numpy as np
from fastapi import APIRouter, Request
from fastapi import Query
from fastapi.responses import HTMLResponse
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import Traces3DPlot , TraceData
from backend.classes.request import RequestPropId, RequestEnvironment
from backend.database.query import query_vms_data, query_vms_parameters
from backend.database.db_connections import ALL_DB_CONNECTIONS

# Create an APIRouter instance
router = APIRouter(prefix="/vms")  

# Example endpoint to check vms status
@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph(request: Request):
    try:
        db_connection = connect_to_user_environment(request)

        current_prop = RequestPropId(request).return_data()
        #Take the data from the prop ID requested
        df = await db_connection.fetch_df(query_vms_data, current_prop)
        
        #Take the parameters from the prop ID requested
        df_params = await db_connection.fetch_df(query_vms_parameters, current_prop)
        
        #Filter the dataframe to only take the data INSIDE the box 
        df = take_data_inside_the_box(df)
        
        #Extra information
        n = len(df) #Number of Samples
        y_vals = np.linspace(0, 570, n) #Space then equally in 570 values (Distance of the box)

        #Load x values for each sensor (Needs to be taken from db, also the height of the sensors) (Temporal solution)
        x_left=df_params.at[0, "offset_l_x"] #Left sensor x value
        x_mid= df_params.at[0, "offset_m_x"] #Middle sensor x value]
        x_right = df_params.at[0, "offset_r_x"] #Right sensor x value
        #Load y values for each sensor (Needs to be taken from db, also the height of the sensors) (Temporal solution)
        y_left= 650 - df_params.at[0, "offset_l_y"] #Left sensor y value
        y_mid = 650 - df_params.at[0, "offset_m_y"] #Middle sensor y value
        y_right = 650 - df_params.at[0, "offset_r_y"] #Right sensor y value   
    
        #Level the sensors to the same height
        df["sensor_l"] = df["sensor_l"] - y_left
        df["sensor_m"] = df["sensor_m"] - y_mid
        df["sensor_r"] = df["sensor_r"] - y_right
        
        #Iterate new values for the material on the wall of the box
        m_left = (df["sensor_m"]-df["sensor_l"])/(x_mid-x_left)
        z_left_zero = m_left * (0- x_left) + df["sensor_l"]

        m_right = (df["sensor_m"]-df["sensor_r"])/(x_mid-x_right)
        z_right_zero = m_right * (367 - x_right) + df["sensor_r"]
        
        #Generate an empty list for traces
        trace_list = []
        #Generate TraceData object and append it
        trace_list.append(TraceData("z0", x_data=np.zeros(n), y_data=y_vals, z_data=np.full(n, 0), color="grey", dash='dot'))
        trace_list.append(TraceData("LeftZero", x_data=np.zeros(n), y_data=y_vals, z_data=z_left_zero, color="black", dash='dot'))
        trace_list.append(TraceData("Left", x_data=np.full(n, x_left), y_data=y_vals, z_data=df["sensor_l"], color="black"))
        trace_list.append(TraceData("Middle", x_data=np.full(n, x_mid), y_data=y_vals, z_data=df["sensor_m"], color="red"))
        trace_list.append(TraceData("Right", x_data=np.full(n, x_right), y_data=y_vals, z_data=df["sensor_r"], color="blue"))
        trace_list.append(TraceData("RightZero", x_data=np.full(n, 367), y_data=y_vals, z_data=z_right_zero, color="blue", dash='dot'))
        trace_list.append(TraceData("z1", x_data=np.full(n, 367), y_data=y_vals,  z_data= np.full(n, 0), color="gray", dash='dot'))

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
    df = df[(df["sensor_m"] < 680) & (df["sensor_m"] > 350)] 
    df = df[(df["sensor_l"] < 680) & (df["sensor_l"] > 350)]
    df = df[(df["sensor_r"] < 680) & (df["sensor_r"] > 350)]
        
    #Inverse the sensors values to have the correct orientation
    df["sensor_l"] = (680 - df["sensor_l"]) 
    df["sensor_m"] = (680 - df["sensor_m"])
    df["sensor_r"] = (680 - df["sensor_r"])

    return df

# ------------ Get the current Environment from the request cookies ---------- #
def connect_to_user_environment(request):
    # Get configuration based on the user's environment
    env_key  = (RequestEnvironment(request).return_data())
    
    if env_key is None or env_key not in ALL_DB_CONNECTIONS:
        print(f"Environment (not) defined as {env_key},  using default configuration.")
        env_key = "CONFIG"  # Default key for DB Connection
    
    # Initialize the DBConnection object with the selected environment
    return  ALL_DB_CONNECTIONS[env_key]