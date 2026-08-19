from collections.abc import Callable, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.doctor import DoctorProfile
from app.models.user import User
from app.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        user_id = int(decode_access_token(credentials.credentials))
    except (InvalidTokenError, ValueError):
        raise unauthorized

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise unauthorized

    return user


def require_roles(*roles: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency


def get_current_doctor_profile(
    current_user: User = Depends(require_roles("doctor")),
    db: Session = Depends(get_db),
) -> DoctorProfile:
    profile = db.scalar(
        select(DoctorProfile).where(DoctorProfile.user_id == current_user.id)
    )
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found",
        )
    return profile
