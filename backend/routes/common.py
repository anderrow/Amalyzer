from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from backend.classes.request import RequestPropId
router = APIRouter(prefix="/common")  

# ---------- Get Actual PropId to analyze ---------- #
@router.get("/PropId")
async def analyzer_status():
    current_prop = RequestPropId().return_data()
    return current_prop