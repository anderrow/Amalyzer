# backend/routes/analyzer.py
from fastapi import APIRouter

# Create an APIRouter instance
router = APIRouter(prefix="/analyzer")  

# Example endpoint to check analyzer status
@router.get("/status")
async def analyzer_status():
    return {"message": "Analyzer endpoint is active"}
