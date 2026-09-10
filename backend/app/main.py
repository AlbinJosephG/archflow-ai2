from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.building import router as building_router


app = FastAPI(
    title="ArchFlow AI API",
    description="Requirement-aware architectural walkthrough generation",
    version="0.1.0"
)


app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)


app.include_router(building_router)


@app.get("/")
def root():

    return {
        "message": "Welcome to ArchFlow AI"
    }


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }