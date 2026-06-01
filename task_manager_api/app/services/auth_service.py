from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from app.utils.hashing import hash_password, verify_password
from app.utils.jwt import create_access_token


def register_user(payload: UserRegister, db: Session) -> UserResponse:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password=hash_password(payload.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse.model_validate(new_user)


def login_user(payload: UserLogin, db: Session) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()

    # intentionally generic message — don't reveal which part is wrong
    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )
