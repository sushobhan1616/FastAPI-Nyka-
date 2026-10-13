
from datetime import datetime, timedelta, timezone
import os

import jwt
from pwdlib import PasswordHash
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field


router = APIRouter()
password_hasher = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)

# Development only. Set a strong secret in your environment.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-this-secret")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30

users = []
next_user_id = 1


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


def create_access_token(user_id: int):
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expires
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    )
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Please log in first"
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    for user in users:
        if user["user_id"] == user_id:
            return user

    raise HTTPException(
        status_code=401,
        detail="User not found"
    )


# REGISTER
@router.post("/register")
def register_user(user: UserRegister):
    global next_user_id

    for existing_user in users:
        if existing_user["username"].lower() == user.username.lower():
            raise HTTPException(
                status_code=409,
                detail="Username already exists"
            )

        if existing_user["email"].lower() == user.email.lower():
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )

    new_user = {
        "user_id": next_user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": password_hasher.hash(user.password)
    }

    users.append(new_user)
    next_user_id += 1

    return {
        "message": "Registration successful",
        "user": {
            "user_id": new_user["user_id"],
            "username": new_user["username"],
            "email": new_user["email"]
        }
    }


# LOGIN
@router.post("/login")
def login_user(user: UserLogin):
    for existing_user in users:
        if (
            existing_user["username"].lower() == user.username.lower()
            and password_hasher.verify(
                user.password,
                existing_user["password_hash"]
            )
        ):
            token = create_access_token(existing_user["user_id"])

            return {
                "message": "Login successful",
                "access_token": token,
                "token_type": "bearer"
            }

    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password"
    )


# GET ALL USERS (public for this learning version)
@router.get("/all")
def get_users():
    return {
        "users": [
            {
                "user_id": user["user_id"],
                "username": user["username"],
                "email": user["email"]
            }
            for user in users
        ]
    }


# GET THE LOGGED-IN USER (requires token)
@router.get("/me")
def get_my_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "email": current_user["email"]
    }
