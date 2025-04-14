# backend/routes/regressor.py
from fastapi import APIRouter

# Create an APIRouter instance
router = APIRouter(prefix="/regressor")  

# Example endpoint to check regressor status
@router.get("/status")
async def regressor_status():
    return {"message": "regressor endpoint is active"}