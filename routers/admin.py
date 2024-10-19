from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from .auth import get_current_user
from models import Users
from pydantic import BaseModel

load_dotenv()

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class Update_role(BaseModel):
    user_id : int
    role: str



# admin can see all users
@router.get("/all_users", status_code=status.HTTP_200_OK)
async def get_all_users(user: user_dependency, db: db_dependency):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return db.query(Users).all()



# admin change user role 
@router.put("/change_role", status_code=status.HTTP_200_OK)
async def change_role(user: user_dependency, db: db_dependency, update_role: Update_role):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_model = db.query(Users).filter(Users.id == update_role.user_id).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_model.role = update_role.role

    db.add(user_model)
    db.commit()

    return {"message": "User role updated successfully", "user_id": update_role.user_id, "new_role": update_role.role}


# admin can delete any user

@router.delete("/delete_user", status_code=status.HTTP_200_OK)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int):
    if user is None or user.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    user_model = db.query(Users).filter(Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(user_model)
    db.commit()

    return {"message": "User deleted successfully", "user_id": user_id}
