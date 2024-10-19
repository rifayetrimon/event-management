from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException, Request
from pydantic import BaseModel
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Event
from .auth import get_current_user
from passlib.context import CryptContext


router = APIRouter(
    prefix="/event",
    tags=["event"],
)



class CreateEventRequest(BaseModel):
    title: str
    description: str
    category: str
    venue: str
    statdate: datetime
    enddate: datetime
    maxcapacity: int
    isprivate: bool



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_event(user: user_dependency, db: db_dependency, event: CreateEventRequest):
    if user is None or user.get("role") != "admin" or user.get("role") != "organizer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    organizer = user.get("id")

    create_event = Event(
        title=event.title,
        description=event.description,
        category=event.category,
        venue=event.venue,
        statdate=event.statdate,
        enddate=event.enddate,
        maxcapacity=event.maxcapacity,
        organizer=organizer,
        isprivate=event.isprivate
    )

    db.add(create_event)
    db.commit()
    db.refresh(create_event)

    return {"message": "Event created successfully"}


