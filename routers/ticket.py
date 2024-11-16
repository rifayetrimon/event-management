from fastapi import APIRouter, Depends, HTTPException, status
from models import Event, Ticket
from pydantic import BaseModel
from enum import Enum
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from routers.auth import get_current_user
from datetime import datetime



router = APIRouter(
    prefix="/ticket",
    tags=["ticket"],
)



class TicketType(str, Enum):
    free = "free"
    paid = "paid"
    vip = "vip"


class CreateTicketRequest(BaseModel):
    event_id: int
    type: TicketType
    price: float
    quantity: int
    available_quantity: int



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]



# create ticket 
@router.post("/create_ticket", status_code=status.HTTP_201_CREATED)
async def create_ticket(user: user_dependency, db: db_dependency, ticket: CreateTicketRequest):
    current_date = datetime.now()

    # Check if user is an admin or organizer
    if user.get("role") not in ['admin', 'organizer']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Fetch the event based on user role
    if user.get("role") == 'admin':
        # Admin can create a ticket for any event that hasn't started yet
        event = db.query(Event).filter(Event.id == ticket.event_id, Event.startdate > current_date).first()
    elif user.get("role") == 'organizer':
        # Organizer can only create tickets for their own events
        event = db.query(Event).filter(Event.id == ticket.event_id, Event.organizer == user.get("id"), Event.startdate > current_date).first()  # Ensure the event hasn't started yet
    
    # Check if the event exists and meets the conditions
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found or you do not have permission to create tickets for this event.")

    # Create and add the ticket
    ticket_model = Ticket(
        event_id=ticket.event_id,
        type=ticket.type,
        price=ticket.price,
        quantity=ticket.quantity,
        available_quantity=ticket.available_quantity    
    )

    db.add(ticket_model)
    db.commit()
    db.refresh(ticket_model)  # Optionally refresh the model to return full data

    return {"message": "Ticket created successfully", "ticket_id": ticket_model.id}




