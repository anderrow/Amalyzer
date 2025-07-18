# backend/routes/settings.py
from fastapi import APIRouter, Request
from fastapi import Query
from backend.database.config import *
from backend.memory.state import session_data
from backend.classes.request import UserInfo

# Create an APIRouter instance
router = APIRouter(prefix="/settings")  


# ----------------- Define a POST routine for selecting environment ----------------- #
@router.post("/selectedenvironment")
async def handle_selected_environmnet(request: Request,  body: UserInfo):
    # Extract UID from the request cookies (More secure than extracting from body)
    uid = request.cookies.get("uid")
    # Extract the Environment from the request body
    #uid = body.uid
    propDbId = body.propDbId
    environment = body.environment

    # Print the UID from the request cookies to the backend console for debugging/logging purposes
    print("\n"+"*"*50+ "\n" + f"* UID:{uid:<43}*")
    # Print the received propDbId to the backend console for debugging/logging purposes
    print("*"*50+ "\n" + f"* Envrionment selected: {environment:<28}*"+ "\n" + "*"*50 + "\n")
    # Check if the session_data dictionary already has an entry for the UID
    # If not, create a new entry for the UID
    if uid not in session_data:
        session_data[uid] = {}

    session_data[uid]["environment"] = environment # Store the propDbId in the session_data dictionary under the UID
    session_data[uid]["current_prop_id"] = None # Reset the propDbId when changing environment (For avoiding request of not existing propDbId)

    return {"environment": environment}