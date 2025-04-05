"""
Main FastAPI application module for the Questions Mentor backend.

This module initializes the FastAPI application and includes the main router
for handling API endpoints.
"""

from fastapi import FastAPI
from backend.app.routes import router

app = FastAPI()

app.include_router(router)
