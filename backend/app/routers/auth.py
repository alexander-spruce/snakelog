import uuid

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.deps import get_current_user
from app.mailer import send_reset_email
from app.models import User
from app.schemas import (
    ChangePassword, ForgotPassword, ProfileUpdate, ResetPassword, Token, UserCreate, UserOut,
)
from app.security import (
    create_access_token, create_reset_token, decode_token, hash_password,
    password_fingerprint, verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Ten e-mail jest już zajęty")
    user = User(email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == form.username.lower()))
    if not user or user.is_blocked or not verify_password(form.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Błędny e-mail lub hasło")
    return Token(access_token=create_access_token(str(user.id)))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user

@router.patch("/me", response_model=UserOut)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Błędne obecne hasło")
    email = data.email.lower()
    taken = db.scalar(select(User).where(User.email == email, User.id != user.id))
    if taken:
        raise HTTPException(status.HTTP_409_CONFLICT, "Ten e-mail jest już zajęty")
    user.email = email
    db.commit()
    db.refresh(user)
    return user


@router.post("/change-password")
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not verify_password(data.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Błędne obecne hasło")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"detail": "Hasło zmienione"}


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(
    data: ForgotPassword,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if user and not user.is_blocked:
        token = create_reset_token(str(user.id), user.password_hash)
        link = f"{settings.frontend_url}/reset-password?token={token}"
        background.add_task(send_reset_email, user.email, link)
    # ta sama odpowiedź niezależnie od istnienia konta, żeby nie ujawniać, kto ma konto
    return {"detail": "Jeśli konto istnieje, wysłaliśmy link do resetu hasła."}


@router.post("/reset-password")
def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    error = HTTPException(status.HTTP_400_BAD_REQUEST, "Link jest nieprawidłowy lub wygasł")
    try:
        payload = decode_token(data.token)
        if payload.get("purpose") != "reset":
            raise ValueError("zły typ tokenu")
        user = db.get(User, uuid.UUID(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise error
    if (
        user is None
        or user.is_blocked
        or payload.get("fp") != password_fingerprint(user.password_hash)
    ):
        raise error
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"detail": "Hasło zmienione. Możesz się zalogować."}