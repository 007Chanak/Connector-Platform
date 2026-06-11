from fastapi import APIRouter
import requests
from sqlalchemy import text
from app.database import engine
from app.database import SessionLocal
import json

from app.services.xero_auth_service import (
    refresh_xero_token
)


from app.config import (
    XERO_CLIENT_ID,
    XERO_CLIENT_SECRET,
    XERO_REDIRECT_URI
)

from app.connectors.dynamics.client import DynamicsClient

router = APIRouter()

@router.get("/test-dynamics")

def test_dynamics():

    client = DynamicsClient()

    data = client.get_customers()

    return data

