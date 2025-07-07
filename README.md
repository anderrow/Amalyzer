# Amalyzer

A web-based analysis and visualization tool for manufacturing proportioning data. Amalyzer helps monitor, analyze, and optimize ingredient handling and proportioning processes.

## Features

- **Proportioning Analysis**: View and filter detailed proportioning records with metrics like dosing accuracy, deviation analysis, and process parameters
- **Real-time Visualization**: Interactive graphs showing:
  - Slide position and control
  - Material dosing
  - Flow rates and control parameters
- **Advanced Analytics**:
  - Regression analysis for flow-position relationships
  - VMS (Vision Measurement System) data visualization
  - Detailed process parameter analysis

## Technologies

- **Backend**: Python FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Data Analysis**: pandas, numpy
- **Visualization**: Plotly

## Project Structure

```
Amalyzer/
├── app.py                  # Main FastAPI application entry point
├── requirements.txt        # Python dependencies
├── run_env.py             # Environment setup script
├── run_server_and_browser.py  # Development server launcher
├── backend/               # Backend application code
│   ├── classes/          # Core business logic classes
│   ├── database/         # Database configuration and queries
│   ├── memory/          # In-memory state management
│   └── routes/          # API route handlers
├── static/               # Frontend assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   ├── images/         # Image assets
│   └── pages/          # HTML pages
```

## Setup and Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure database connection in `backend/database/config.py`
5. Run the application:
   ```bash
   python run_server_and_browser.py
   ```

## Key Components

### Backend

- **FastAPI Application**: Provides RESTful API endpoints for data retrieval and analysis
- **Database Connection**: Manages PostgreSQL database interactions
- **Data Processing**: Handles calculations, filtering, and data transformation
- **Graph Generation**: Creates interactive visualizations using Plotly

### Frontend

- **Interactive Dashboard**: Real-time data visualization and analysis tools
- **Responsive Design**: Mobile-friendly interface
- **Data Filtering**: Dynamic data filtering and sorting capabilities
- **Multi-page Layout**: Separate views for different analysis tools:
  - Proportionings overview
  - Analyzer with detailed graphs
  - Regression analysis
  - VMS visualization

## Development

The project follows a modular architecture:

- Route handlers in `backend/routes/` handle API endpoints
- Business logic is encapsulated in classes under `backend/classes/`
- Database queries are centralized in `backend/database/query.py`
- Frontend JavaScript modules handle page-specific functionality

## Dependencies

See `requirements.txt` for a complete list of Python dependencies. Key packages include:

- fastapi
- numpy
- pandas
- plotly
- psycopg2_binary
- uvicorn
- SQLAlchemy