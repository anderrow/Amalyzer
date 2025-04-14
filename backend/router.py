# backend/router.py
from fastapi import APIRouter

# Import routers from each module in the routes folder
from backend.routes import proportionings, analyzer, regressor, vms

# Create a global APIRouter instance
router = APIRouter()

# Include routers from each module
router.include_router(proportionings.router)   #  "Include routes from proportionings module"
router.include_router(analyzer.router)         #  "Include routes from analyzer module"
router.include_router(regressor.router)        #  "Include routes from regressor module"
router.include_router(vms.router)              #  "Include routes from vms module"

