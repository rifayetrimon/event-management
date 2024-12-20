from typing import Optional
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, Field
from models import Users
from typing import Optional, Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import SessionLocal
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
import os



load_dotenv()


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

# for jwt algorithoms

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token") 




# authenticate user

def authenticate_user(email: str, password: str, db):
    user = db.query(Users).filter(Users.email == email).first()

    if not user:
        return False

    if not bcrypt_context.verify(password, user.password):
        return False

    return user


# create user access tokenn 

def create_access_token(name: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {"sub": name, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)



# get current user 

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email: str = payload.get("sub")
        user_id: int = payload.get("id")
        role: str = payload.get("role")

        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        return {"email": email, "id": user_id, "role": role}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")




# pytdantic schema

class CreateUserRequest(BaseModel):
    name: str
    email: str = Field(unique=True)
    password: str
    role: Optional[str] = None 
    phone_number: str



class Token(BaseModel):
    access_token: str
    token_type: str



# db connection 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]




#  Create a new User object with the provided information and hashed password

@router.post("/signup", status_code= status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user: CreateUserRequest):

    existing_user = db.query(Users).filter(Users.email == create_user.email).first()
    
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    crete_user_model = Users(
        name = create_user.name,
        email = create_user.email,
        password = bcrypt_context.hash(create_user.password),
        role = create_user.role,
        phone_number = create_user.phone_number
    )
    
    db.add(crete_user_model)
    db.commit()
    
    return {"message": "User created successfully"}
    


@router.post("/token", response_model=Token)
async def access_token_for_login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency,):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=20))
    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(user.email, user.id, user.role, timedelta(minutes=20))

    return {"access_token": token, "token_type": "bearer"}

    