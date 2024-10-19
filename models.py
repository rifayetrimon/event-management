from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func




########## User model 
class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String)
    phone_number = Column(String)
    date_created = Column(DateTime(timezone=True), server_default=func.now())


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    venue = Column(String)
    statdate = Column(DateTime)
    enddate = Column(DateTime)
    maxcapacity = Column(Integer)
    organizer = Column(ForeignKey("users.id"))
    isprivate = Column(Boolean)

