import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.app.database import Base, engine
from backend.app.routers import cases, matches, graph, dashboard, audit

# Ensure DB tables exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Rakshak Link API",
    description="Cross-District Missing Person & Trafficking Intelligence System",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(cases.router)
app.include_router(matches.router)
app.include_router(graph.router)
app.include_router(dashboard.router)
app.include_router(audit.router)

@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "Rakshak Link API"}

# Serve frontend build if dist folder exists
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
