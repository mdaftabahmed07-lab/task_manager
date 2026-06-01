from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Create a new user account.

    - **full_name**: Your display name
    - **email**: Must be a valid, unique email address
    - **password**: Minimum 8 characters
    """
    return register_user(payload, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Log in and receive a JWT access token.

    Use the token in subsequent requests as:
    `Authorization: Bearer <token>`
    """
    return login_user(payload, db)
