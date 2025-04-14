# backend/routes/vms.py
from fastapi import APIRouter

# Create an APIRouter instance
router = APIRouter(prefix="/vms")  

# Example endpoint to check vms status
@router.get("/status")
async def vms_status():
    return {"message": "vms endpoint is active"}