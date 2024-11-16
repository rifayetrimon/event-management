from pydantic import BaseModel, Field
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from passlib.context import CryptContext
from models import Users


router = APIRouter(
    prefix="/users",
    tags=["users"],
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


class UpdateUser(BaseModel):
    name: str
    email: str
    phone_number: str



@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return db.query(Users).filter(Users.id == user.get("id")).first()


# user password change 

@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")   
    
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    if not bcrypt_context.verify(user_verification.password, user_model.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password Change !")
    
    user_model.password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


# update user info

@router.put("/change_info", status_code=status.HTTP_200_OK)
async def update_user(user: user_dependency, db: db_dependency, update_user: UpdateUser):

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Retrieve the user from the database
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    # Store the previous data you want to show before the update
    previous_data = {
        "name": user_model.name,
        "email": user_model.email,
        "phone_number": user_model.phone_number,
        "role": user_model.role,
        "date_created": user_model.date_created
    }

    # Update the user model with new information
    user_model.name = update_user.name
    user_model.email = update_user.email
    user_model.phone_number = update_user.phone_number
    
    # Commit the updated user info to the database
    db.add(user_model)
    db.commit()

    return {
        "message": "User information updated successfully!",
        "previous_data": previous_data,
        "updated_data": {
            "name": user_model.name,
            "email": user_model.email,
            "phone_number": user_model.phone_number,
            "role": user_model.role
        }
    }
    


# delete user 
    
@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()

    db.delete(user_model)
    db.commit()
    return {"message": "User deleted successfully"}

