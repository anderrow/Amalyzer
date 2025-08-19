# backend/routes/settings.py
from fastapi import APIRouter, Request
from backend.memory.state import session_data
from backend.classes.request import UserInfo
from backend.database.config import env_map

# Create an APIRouter instance
router = APIRouter(prefix="/settings")  


# ----------------- Define a POST routine for selecting environment ----------------- #
@router.post("/selectedenvironment")
async def handle_selected_environmnet(request: Request,  body: UserInfo):
    # Extract UID from the request cookies (More secure than extracting from body)
    uid = request.cookies.get("uid")
    # Extract the Environment from the request body
    environment = body.environment
    
    rows = body.rows

    # Print the UID from the request cookies to the backend console for debugging/logging purposes
    print("\n"+"*"*50+ "\n" + f"* UID:{uid:<43}*")
    # Print the received propDbId to the backend console for debugging/logging purposes
    print("*"*50+ "\n" + f"* Envrionment selected: {environment:<26}*"+ "\n" + "*"*50 )
    print(f"*Rows selected: {rows:<37}*"+ "\n" + "*"*50 + "\n")

    # Check if the session_data dictionary already has an entry for the UID
    # If not, create a new entry for the UID
    if uid not in session_data:
        session_data[uid] = {}

    session_data[uid]["environment"] = environment # Store the propDbId in the session_data dictionary under the UID
    session_data[uid]["current_prop_id"] = None # Reset the propDbId when changing environment (For avoiding request of not existing propDbId)

    return {"environment": environment}



@router.get("/availableenvironments")
async def get_available_environments():
    #Get a list of the env defined in the config.py
    env_list = list(env_map.keys())
    
    return env_list