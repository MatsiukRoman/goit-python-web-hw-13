from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from starlette import status

from src.database.db import get_db
from src.entity.models import User
from src.conf.config import settings


class Hash:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)


class Auth:
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=expires_delta or 900)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=expires_delta or 604800)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    async def get_email_form_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload.get("scope") != "refresh_token":
                raise HTTPException(status_code=401, detail="Invalid scope for token")
            return payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = db.query(User).filter(User.email == email).first()
        if user is None:
            raise credentials_exception
        return user

    def get_user_by_email(self, email: str, db: Session):
        return db.query(User).filter_by(email=email).first()

    def confirmed_email(self, email: str, db: Session):
        user = self.get_user_by_email(email, db)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.email_verified = True
        db.commit()

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=422, detail="Invalid token for email verification")


auth_service = Auth()
