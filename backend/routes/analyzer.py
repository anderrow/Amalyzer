from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import plotly.io as pio
import plotly.graph_objects as go
from backend.memory.state import session_data
from backend.classes.db_connection import DBConnection
from backend.database.config import config
from backend.database.query import query_analyzer_summary, query_analyzer_propRecord, query_analyzer_logginParam, query_analyzer_lot, query_analyzer_article
# Create an APIRouter instance
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
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_summary.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)

        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ---------- PROP RECORD ---------- #    
@router.get("/PropRecord")
async def propRecord_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_propRecord.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ---------- Logging Param ---------- #    
@router.get("/LogginParam")
async def propRecord_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_logginParam.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# ---------- Logging Param ---------- #    
@router.get("/Lot")
async def lot_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_lot.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    
# ---------- Logging Param ---------- #    
@router.get("/Article")
async def article_table():
    try:
        #Get current proportioning id
        current_prop = session_data.get("current_prop_id")
        #Write the current_prop variable inside the query
        query = query_analyzer_article.format(current_prop=current_prop)
        #Request the data
        data = await db_connection.fetch_data(query=query)
        
        return data
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}
    

# ---------- Generate and return interactive graph ---------- #
@router.get("/Graph", response_class=HTMLResponse)
async def generate_graph():
    try:
        # Datos de ejemplo
        x_values = [0, 10, 20, 30, 40, 50]
        y_values = [100] * len(x_values)

        # Crear el gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_values, y=y_values, mode='lines', name='Line at 100'))
        fig.update_layout(
            title="Horizontal Line at 100",
            xaxis_title="X Axis",
            yaxis_title="Y Axis",
            template="plotly_dark"
        )

        # Convertir el gráfico a HTML
        graph_html = pio.to_html(fig, full_html=False)

        # Retornar HTML crudo (sin serializar a JSON)
        return graph_html

    except Exception as e:
        print(f"Error: {e}")
        # Aquí podrías devolver un HTML de error, o un JSON si prefieres
        return HTMLResponse(f"<p>Error generating graph: {e}</p>", status_code=500)

    
# ---------- Serve the HTML page with embedded graph ----------
@router.get("/", response_class=HTMLResponse)
async def show_page():
    try:
        # Get the interactive graph HTML from the generate_graph function
        graph_html = await generate_graph()

        # Return the HTML page with the embedded graph
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
    except Exception as e:
        return f"Error: {str(e)}"