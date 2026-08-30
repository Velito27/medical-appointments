from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import get_current_user, get_db
from app.models.login_history import LoginHistory
from app.models.user import User
from app.schemas import AdminLogin, TokenResponse, UserLogin, UserRegister, UserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


def record_login(db: Session, user: User) -> None:
    db.add(LoginHistory(user_id=user.id))
    db.commit()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(data: UserRegister, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()
    existing_user = db.scalar(select(User).where(User.email == email))
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=email,
        password_hash=hash_password(data.password),
        role="patient",
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    email = str(data.email).strip().lower()
    user = db.scalar(select(User).where(User.email == email))

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is inactive")

    record_login(db, user)

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        user=user,
    )


@router.post("/admin-login", response_model=TokenResponse)
def admin_login(data: AdminLogin, db: Session = Depends(get_db)):
    if data.username.strip().lower() != settings.admin_username.strip().lower():
        raise HTTPException(status_code=401, detail="Admin o clave incorrectos")

    admin = db.scalar(
        select(User).where(
            User.email == settings.admin_email.strip().lower(),
            User.role == "admin",
        )
    )

    if admin is None or not verify_password(data.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Admin o clave incorrectos")

    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Cuenta de administrador inactiva")

    record_login(db, admin)

    return TokenResponse(
        access_token=create_access_token(str(admin.id)),
        user=admin,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
