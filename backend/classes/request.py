from pydantic import BaseModel

# Import BaseModel from Pydantic to define the expected structure of the request body
class PropIdRequest(BaseModel):
    # This field represents the ID of the selected row, expected to be an integer
    propDbId: int
