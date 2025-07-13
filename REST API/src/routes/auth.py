from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.entity.models import User
from src.database.db import get_db
from src.services.auth import auth_service, Hash
from src.services.email import send_email
from src.schemas.schemas import UserModel

router = APIRouter(prefix="/auth", tags=["auth"])

hash_handler = Hash()
security = HTTPBearer()

@router.post("/signup")
async def signup(body: UserModel, bt: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    exist_user = db.query(User).filter(User.email == body.email).first()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    new_user = User(username=body.username,  email=body.email, password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # send email notification
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return {"new_user": new_user.email}

@router.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email!")
    if not user.email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not verified!")
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password!")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.get_email_form_refresh_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/secret")
async def read_item(current_user: User = Depends(auth_service.get_current_user)):
    return {"message": 'secret router', "owner": current_user.email}

@router.get("/confirmed_email/{token}")
def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = auth_service.get_email_from_token(token)
    user = auth_service.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    
    if user.email_verified:
        return {"message": "Your email is already confirmed"}

    auth_service.confirmed_email(email, db)
    return {"message": "Email confirmed"}