from fastapi import FastAPI
import models
from database import engine
from routers import auth, users, admin, event, ticket, registration
import uvicorn
import logging
import os


app = FastAPI()



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup_event():
    try:
        logger.info("Creating tables...")
        models.Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")



# models.Base.metadata.create_all(bind=engine)


# connect all routers here 

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(admin.router)
app.include_router(event.router)
app.include_router(ticket.router)
app.include_router(registration.router)




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=int(10000))