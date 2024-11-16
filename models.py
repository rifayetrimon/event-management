from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func





########## User model 
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    phone_number = Column(String, unique=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())




# event table model
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    venue = Column(String)
    startdate = Column(DateTime)
    enddate = Column(DateTime)
    maxcapacity = Column(Integer)
    organizer = Column(ForeignKey("users.id"))
    isprivate = Column(Boolean)



# ticket table model

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(ForeignKey("events.id"))
    type = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    available_quantity = Column(Integer)