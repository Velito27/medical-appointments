from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import check_database_connection
from app.routers import admin, appointments, auth, doctor, public


app = FastAPI(
    title="Medical Appointments API",
    version="1.0.0",
    description="API for patients, doctors and administrators to manage medical appointments.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(public.router)
app.include_router(appointments.router)
app.include_router(doctor.router)
app.include_router(admin.router)


@app.get("/")
def root():
    return {
        "name": "Medical Appointments API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check():
    try:
        check_database_connection()
        return {
            "status": "ok",
            "database": "connected",
        }
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )
