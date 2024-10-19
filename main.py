from fastapi import FastAPI
import models
from database import engine
from routers import auth, users, admin, event


app = FastAPI()

# models connects to the database

models.Base.metadata.create_all(bind=engine)


# connect all routers here 

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(event.router)