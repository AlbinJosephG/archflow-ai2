
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.room import router as room_router


app = FastAPI(
    title="ArchFlow AI",
    description="AI-powered single-room architectural design and visualization",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Register only the single-room API
app.include_router(room_router)


@app.get("/")
def root():
    return {
        "message": "Welcome to ArchFlow AI - Single Room Design"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
