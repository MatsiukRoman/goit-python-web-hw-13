from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional

class ContactSchema(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: str

class ContactResponse(ContactSchema):
    id: int = 1

    class Config:
       from_attributes = True

class UserModel(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: Optional[str] = None
    email_verified: bool

    class Config:
        from_attributes = True