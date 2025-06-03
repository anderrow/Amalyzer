from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.router import router  
import uvicorn

app = FastAPI()

# Serve frontend from the /frontend path (e.g., http://localhost:8000/static/index.html)
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

# Include API routes
app.include_router(router)

# Enable CORS (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Start the app with uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
