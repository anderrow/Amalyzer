# backend/routes/analyzer.py
from fastapi import APIRouter
from backend.classes.memory.state import session_data

# Create an APIRouter instance
router = APIRouter(prefix="/analyzer")  

# Get Actual PropId to analyze
@router.get("/PropId")
async def analyzer_status():
    current_prop = session_data.get("current_prop_id")
    return current_prop

