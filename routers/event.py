from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from models import Event, Users
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
    startdate: datetime
    enddate: datetime
    maxcapacity: int
    isprivate: bool


class UpdateEventRequest(BaseModel):
    event_id: int
    title: str
    description: str
    category: str
    venue: str
    startdate: datetime
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


# create_event
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_event(user: user_dependency, db: db_dependency ,event: CreateEventRequest):
    if user.get("role") == 'admin' or user.get("role") == 'organizer':

        organizer_id = user.get("id")

        create_event = Event(
            title=event.title,
            description=event.description,
            category=event.category,
            venue=event.venue,
            startdate=event.startdate,
            enddate=event.enddate,
            maxcapacity=event.maxcapacity,
            organizer=organizer_id,
            isprivate=event.isprivate
        )

        db.add(create_event)
        db.commit()
        db.refresh(create_event)

        return {"message": "event created successfully"}

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")





# view event  if viewer is admin can see all if organizer can see only his

@router.get("/view_event", status_code=status.HTTP_200_OK)
async def view_event(user: user_dependency, db: db_dependency):
    if user.get("role") == 'admin':
        events = db.query(Event).all()
        return events
    elif user.get("role") == 'organizer':
        events = db.query(Event).filter(Event.organizer == user.get("id")).all()
        return events
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    


# here admin can update any event but organizer can only update his event

@router.put("/update_event", status_code=status.HTTP_200_OK)
async def update_event(user: user_dependency, db: db_dependency, event: UpdateEventRequest):

    if user.get("role") == 'admin':
        event_model = db.query(Event).filter(Event.id == event.event_id).first()

        if not event_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        event_model.title = event.title
        event_model.description = event.description
        event_model.category = event.category
        event_model.venue = event.venue
        event_model.startdate = event.startdate
        event_model.enddate = event.enddate
        event_model.maxcapacity = event.maxcapacity
        event_model.isprivate = event.isprivate

        db.add(event_model)
        db.commit()
        db.refresh(event_model)

        return {"message": "event updated successfully", "new_data": event_model}

    elif user.get("role") == 'organizer':

        event_model = db.query(Event).filter(Event.organizer == user.get("id")).first()
        
        if not event_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        event_model.title = event.title
        event_model.description = event.description
        event_model.category = event.category    
        event_model.venue = event.venue
        event_model.startdate = event.startdate
        event_model.enddate = event.enddate
        event_model.maxcapacity = event.maxcapacity
        event_model.isprivate = event.isprivate

        db.add(event_model)
        db.commit()
        db.refresh(event_model)

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


# admin can delete any event but organizer can only delete his event

@router.delete("/delete_event", status_code=status.HTTP_200_OK)
async def delete_event(user: user_dependency, db: db_dependency, event_id: int):

    if user.get("role") == 'admin':
        event_model = db.query(Event).filter(Event.id == event_id).first()

        if not event_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        db.delete(event_model)
        db.commit()
        db.refresh(event_model)

        return {"message": "event deleted successfully"}

    elif user.get("role") == 'organizer':
        event_model = db.query(Event).filter(Event.organizer == user.get("id")).first()

        if not event_model:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")

        db.delete(event_model)
        db.commit()
        db.refresh(event_model)

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")