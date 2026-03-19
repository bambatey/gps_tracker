from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .datalayer.database import create_tables
from .routes import device_routes, track_routes


app = FastAPI(title="GPS Tracker API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(device_routes.router)
app.include_router(track_routes.router)


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/track")
async def track():
    return FileResponse("static/tracker.html")


@app.on_event("startup")
async def startup_event():
    create_tables()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
