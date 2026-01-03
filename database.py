from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

#Load environment variables from .env file
load_dotenv()

#Get Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

#Create databse engine(the connection manager)
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
    )

#Create Session factory (for talking to database)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


#Base class for all our database models
Base = declarative_base()

#Function to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
