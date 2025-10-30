# from fastapi import FastAPI, Depends, HTTPException, Header
# from .schemas import CheckoutEvent
# from .auth import create_jwt_token, verify_jwt
# from .tasks import process_checkout
# from .db import engine, Base, SessionLocal
# from .models import Guest
# from fastapi.security import OAuth2PasswordRequestForm
# from pydantic import BaseModel
# from typing import Dict
# import os
# from dotenv import load_dotenv
# load_dotenv()

# Base.metadata.create_all(bind=engine)

# app = FastAPI(title="Reconnect AI - FastAPI (FAISS)")

# SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "our-secret-key")
# MANAGER_USER = "manager"
# MANAGER_PASS = "password"

# @app.post("/events/guest-checkout", status_code=202)
# def guest_checkout(event: CheckoutEvent, x_api_key: str = Header(...)):
#     if x_api_key != SERVICE_API_KEY:
#         raise HTTPException(status_code=401, detail="Invalid API key")
#     payload = event.dict()
#     process_checkout.delay(payload)
#     return {"status": "accepted"}

# @app.post("/mock-api/send-notification")
# def mock_send_notification(payload: Dict):
#     print("Mock notification payload:", payload)
#     return {"status": "mock_sent", "detail": payload}

# class TokenResponse(BaseModel):
#     access_token: str
#     token_type: str = "bearer"

# @app.post("/token", response_model=TokenResponse)
# def token(form_data: OAuth2PasswordRequestForm = Depends()):
#     if form_data.username == MANAGER_USER and form_data.password == MANAGER_PASS:
#         token = create_jwt_token(form_data.username)
#         return {"access_token": token}
#     raise HTTPException(status_code=401, detail="Bad credentials")

# # def get_current_user(authorization: str = Header(..., alias="Authorization")):
# #     if not authorization.startswith("Bearer "):
# #         raise HTTPException(status_code=401, detail="Invalid auth header")
# #     token = authorization.split(" ", 1)[1]
# #     payload = verify_jwt(token)
# #     return payload
# def get_current_user(authorization: str = Header(..., alias="Authorization")):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=401, detail="Invalid auth header")
#     token = authorization.split(" ", 1)[1]
#     payload = verify_jwt(token)
#     return payload
# @app.get("/guest-profile/{guest_id}")
# def guest_profile(guest_id: str, user=Depends(get_current_user)):
#     db = SessionLocal()
#     try:
#         guest = db.query(Guest).filter_by(guest_id=guest_id).one_or_none()
#         if not guest:
#             raise HTTPException(status_code=404, detail="Guest not found")
#         profile = {
#             "guest_id": guest.guest_id,
#             "total_lifetime_spend": guest.total_lifetime_spend,
#             "average_sentiment": guest.average_sentiment,
#             "stays_count": guest.stays_count,
#             "last_stay_date": guest.last_stay_date.isoformat() if guest.last_stay_date else None,
#             "metadata": guest.metadata
#         }
#         return profile
#     finally:
#         db.close()
from fastapi import FastAPI, Depends, HTTPException, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from .schemas import CheckoutEvent
from .auth import create_jwt_token, verify_jwt
from .tasks import process_checkout
from .db import engine, Base, SessionLocal
from .models import Guest
from pydantic import BaseModel
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reconnect AI - FastAPI (FAISS)")

# App-level configuration
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "our-secret-key")
MANAGER_USER = "manager"
MANAGER_PASS = "password"

# Security Scheme for Swagger UI
security = HTTPBearer()  # enables "Authorize" button automatically

# Routes
@app.post("/events/guest-checkout", status_code=202)
def guest_checkout(event: CheckoutEvent, x_api_key: str = Header(...)):
    if x_api_key != SERVICE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    payload = event.dict()
    process_checkout.delay(payload)
    return {"status": "accepted"}


@app.post("/mock-api/send-notification")
def mock_send_notification(payload: Dict):
    print("Mock notification payload:", payload)
    return {"status": "mock_sent", "detail": payload}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/token", response_model=TokenResponse)
def token(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username == MANAGER_USER and form_data.password == MANAGER_PASS:
        token = create_jwt_token(form_data.username)
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Bad credentials")


# Authentication Dependency 
def get_current_user(authorization: str = Header(..., alias="Authorization")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")
    token = authorization.split(" ", 1)[1]
    payload = verify_jwt(token)
    return payload


# Guest Profile Endpoint (protected)
@app.get("/guest-profile/{guest_id}")
def guest_profile(
    guest_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """
    Retrieve guest profile by ID. Requires Bearer token authentication.
    """
    token = credentials.credentials
    payload = verify_jwt(token)

    db = SessionLocal()
    try:
        guest = db.query(Guest).filter_by(guest_id=guest_id).one_or_none()
        if not guest:
            raise HTTPException(status_code=404, detail="Guest not found")

        profile = {
            "guest_id": guest.guest_id,
            "total_lifetime_spend": guest.total_lifetime_spend,
            "average_sentiment": guest.average_sentiment,
            "stays_count": guest.stays_count,
            "last_stay_date": guest.last_stay_date.isoformat() if guest.last_stay_date else None,
            "metadata": guest.metadata
        }
        return profile
    finally:
        db.close()
