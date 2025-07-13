from datetime import  datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional

from slowapi import Limiter
from slowapi.util import get_remote_address

from sqlalchemy import text, extract, or_, and_
from src.entity.models import User, Contact
from src.database.db import get_db
from src.services.auth import auth_service
from src.schemas.schemas import ContactSchema, ContactResponse, UserModel

router = APIRouter(prefix="/contacts", tags=["contacts"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/contacts", response_model=list[ContactResponse])
def get_contacts(
    current_user: User = Depends(auth_service.get_current_user), 
    first_name: Optional[str] = Query(None, title="First Name"),
    last_name: Optional[str] = Query(None, title="Last Name"),
    email: Optional[str] = Query(None, title="Email"),
    db: Session = Depends(get_db),
):
    query = db.query(Contact).filter(Contact.user_id == current_user.id)

    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    contacts = query.all()
    return contacts

@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(
    contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)
):
    # contact = db.query(Contact).filter_by(id=contact_id).first()
    contact = db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact

@router.post("/contacts", response_model=ContactResponse)
@limiter.limit("3/minute")
async def create_contact(request: Request, body: ContactSchema, current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(email=body.email).first()
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Contact already exists!"
        )

    contact = Contact(**body.model_dump(),user_id=current_user.id) 
    db.add(contact)
    db.commit()
    return contact

@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactSchema, contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)
):
    contact = db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    contact.first_name = body.first_name
    contact.last_name = body.last_name
    contact.email = body.email
    contact.phone_number = body.phone_number
    contact.birthday = body.birthday
    contact.additional_info = body.additional_info

    db.commit()
    return contact


@router.delete("/contacts/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int = Path(ge=1), current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id, user_id=current_user.id).first()
    
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")

    db.delete(contact)
    db.commit()
    return contact

@router.get("/contacts/upcoming-birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    today = datetime.now().date()
    end_date = today + timedelta(days=7)

    if today.month == 12 and end_date.month == 1:
        contacts = (
            db.query(Contact)
            .filter(
                or_(
                    extract("month", Contact.birthday) == today.month,
                    extract("day", Contact.birthday) >= today.day,
                    extract("month", Contact.birthday) == end_date.month,
                    extract("day", Contact.birthday) <= end_date.day,
                )
            )
            .filter(Contact.user_id == current_user.id)
            .all()
        )
    else:
        contacts = (
            db.query(Contact)
            .filter(
                or_(
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == end_date.month,
                        extract("day", Contact.birthday) <= end_date.day,
                    ),
                )
            )
            .filter(Contact.user_id == current_user.id)
            .all()
        )

    return contacts
