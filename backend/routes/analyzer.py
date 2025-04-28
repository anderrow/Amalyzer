from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import pandas as pd
import psycopg2
from backend.memory.state import session_data
from backend.classes.db_connection import DBConnection
from backend.classes.graphs import PlotPointsinTime
from backend.database.config import config
from backend.database.query import query_analyzer_summary, query_analyzer_propRecord, query_analyzer_logginParam, query_analyzer_lot, query_analyzer_article, query_analyzer_slide_graph
router = APIRouter(prefix="/analyzer")  

# Initialize the DBConnection object
db_connection = DBConnection(config=config) #config is declared in backend/database/config.py

# Get Actual PropId to analyze
@router.get("/PropId")
async def analyzer_status():
    current_prop = session_data.get("current_prop_id")
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
    

# ---------- Generate and return interactive graph ---------- #
@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph():
    try:
        df = await db_connection.fetch_df(query=query_analyzer_slide_graph)
       
        graph_html = PlotPointsinTime(
            session_data.get("current_prop_id"), 
            title="Slide Position", 
            xaxis_title="Seconds", 
            yaxis_title="mm", 
            sample_time=0.01, 
            x_axis=df.index.to_list(), 
            y_axis=df["plant_out_slideposition"].to_list()
        ).plot_graph()

        # Return raw HTML
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Aquí podrías devolver un HTML de error, o un JSON si prefieres
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)

    
# ---------- Serve the HTML page with embedded graph ---------- #
@router.get("/", response_class=HTMLResponse)
async def show_page():
    try:
        # Get the interactive graph HTML from the generate_graph function
        graph_html = await generate_graph()

        # Return the HTML page with the embedded graph
        return embebbed_graph(graph_html)
    
    except Exception as e:
        return f"Error: {str(e)}"

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
    

def embebbed_graph(graph_html):
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Interactive Graph</title>
    </head>
    <body>
        <h1>Graph</h1>
        <section id="AnalyzerGraphs">
            {graph_html}  <!-- The interactive graph is inserted here -->
        </section>
    </body>
    </html>
    """