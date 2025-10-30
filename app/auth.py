import os
from dotenv import load_dotenv
from fastapi import Header, HTTPException, Depends
from jose import jwt
from datetime import datetime, timedelta
load_dotenv()
SERVICE_API_KEY = os.getenv("SERVICE_API_KEY", "our-secret-key")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "supersecretjwtkey")
ALGORITHM = "HS256"
MANAGER_USER = "manager"
MANAGER_PASS = "password"

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != SERVICE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

def create_jwt_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=4)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)
    return token

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
