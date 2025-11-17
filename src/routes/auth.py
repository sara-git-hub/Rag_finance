from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from helpers.auth import create_access_token, verify_password, get_current_user, require_admin
from models.UserModel import UserModel
from models.db_schemes.minirag.schemes.user import UserRole

import logging

logger = logging.getLogger('uvicorn.error')

auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["authentication"],
)

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    is_active: bool

@auth_router.post("/register", response_model=Token)
async def register(request: Request, register_data: RegisterRequest):
    """Register a new user. First user automatically becomes admin."""
    user_model = UserModel(db_client=request.app.db_client)

    # Check if username exists
    existing_user = await user_model.get_user_by_username(register_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Check if email exists
    existing_email = await user_model.get_user_by_email(register_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user (first user will be admin automatically)
    user = await user_model.create_user(
        username=register_data.username,
        email=register_data.email,
        password=register_data.password
    )

    # Generate token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=timedelta(hours=24)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "username": user.username
    }

@auth_router.post("/login", response_model=Token)
async def login(request: Request, login_data: LoginRequest):
    """Login with username and password."""
    user_model = UserModel(db_client=request.app.db_client)

    user = await user_model.get_user_by_username(login_data.username)

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=timedelta(hours=24)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "username": user.username
    }

@auth_router.get("/me", response_model=UserResponse)
async def get_current_user_info(request: Request, current_user: dict = Depends(get_current_user)):
    """Get current logged-in user information."""
    user_model = UserModel(db_client=request.app.db_client)
    user = await user_model.get_user_by_username(current_user["username"])

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return {
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active
    }

@auth_router.get("/users", response_model=list[UserResponse])
async def get_all_users(request: Request, current_user: dict = Depends(require_admin)):
    """Get all users (admin only)."""
    user_model = UserModel(db_client=request.app.db_client)
    users = await user_model.get_all_users()

    return [
        {
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active
        }
        for user in users
    ]
