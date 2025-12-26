# Simple Todo API - Perfect for Beginners
# Copy this code, run it, and understand each part

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import engine
from models import Base
from sqlalchemy.orm import Session
from database import get_db
import models
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth import verify_password, get_password_hash, create_access_token, verify_token
from datetime import timedelta

security = HTTPBearer()

Base.metadata.create_all(bind=engine)


# Create the FastAPI app
app = FastAPI(title= 'Simple To Do App', description= 'Beginner App for Practice')

# What a complete Todo looks like (for responses)
class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime

# What users send when CREATING a todo (no id, no created_at)
class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None

# What users send when UPDATING a todo (all optional)
class TodoUpdate(BaseModel):
    title: Optional[str] = None 
    description: Optional[str] = None
    completed: Optional[bool] = None

class TodoToggle(BaseModel):
    message: str
    todo: Todo

class UserCreate(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    created_at: datetime

    class config:
        from_atributes: True
    
class Token(BaseModel):
    access_token: str
    token_type:  str

class UserLogin(BaseModel):
    email: str
    password: str


#Helper function to get current user from token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user from the token"""
    token = credentials.credentials
    email = verify_token(token)
    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None:
        raise HTTPException(status=400, detail="User not found")
    return user


#Authentication Endpoints

@app.post("/auth/register", response_model =UserResponse)
def register(user_data = UserCreate, db: Session = Depends(get_db)):
    """Register New User"""
    #check existing user
    existing_user = db.query(models.User).filter(models.User.email==user_data.email).first
    if existing_user:
        raise HTTPException (status_code = 400, detail = "Email already registered")

    #create new user
    hashed_password = get_password_hash(user_data.hash)
    new_user = models.User(
        email = user_data.email,
        hashed_password = hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/auth/login", response_model=Token)
def login(user_data = UserLogin ,db: Session = Depends(get_db)):
    """Existing User Login"""""
    #check if user email  is in databse
    existing_email = db.query(models.User).filter(models.User.email==user_data.email).first()
    if not existing_email:
        raise HTTPException(status_code=401, detail ="Email is not registered")

    #if it is then verify password
    if not verify_password(user_data.password==User.hashed_password):
        raise HTTPException (status_code=401, detail = "Incorrect Email or Password")

    
    #create token if email is in the database
     
    new_token = create_access_token(
        data = {sub: 'user_data.email'},
        expires_delta = timedelta(minutes=120)
    )

    return {"access_token": access_token, "token_type": "Bearer"}

# get info for current user

@app.get("/auth/me")
def get_current_user_info(current_user: models.User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


# Root endpoint - Welcome message
@app.get("/")
def read_root():
    return {
        "message":"Welcome to the Todo App API",
        "endpoints": [
            # crud operations
            "Get/todos - Get all todos",
            "Get/todos/{todo_id} - Get a sepcific todo",
            "Post/todos -  Create a new todo",
            "Put/todos/{todo_id} - Update a todo",
            "Delete /todo/{todo_id} - Delete a todo"
            
            # Filtering
            "Get/todos/completed - Get completed todos",
            "Get/todos/pending - Get pending todos",

            # Quick Actions
            "Patch/todos/{todo_id}/toggle - Mark a todo complete or incomplete",

            # Analytics
            "Get/stats - Get todo stats"
        ]
    }

# Get all todos
@app.get("/todos", response_model=List[Todo])
def get_todos(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get all todos for current user"""
    return db.query(models.Todo).filter(models.Todo.owner_id==current_user.id).all()

# Get a specific todo by ID
@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.owner_id==current_user.id, models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status=404, detail = "Todo not found")
    return db_todo
     

# Create a new todo
@app.post("/todos/", response_model=Todo)
def create_todo(todo_data: TodoCreate, current_user : models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    db_todo = models.Todo(
        title= todo_data.title,
        description= todo_data.description,
        owner_id = current_user.id
        )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)

    return db_todo

# Update an existing todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, updates: TodoUpdate, current_user : models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.owner_id==current_user.id, models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException (status_code=404, detail= "Todo not found")

    if updates.title is not None:
        db_todo.title = updates.title
    if updates.description is not None:
        db_todo.description = updates.description
    if updates.completed is not None:
        db_todo.completed = updates.completed
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Delete todo

@app.delete("/todos/{todo_id}", response_model=Todo)
def delete_todo(todo_id:int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.owner_id == current_user.id, models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(db_todo)
    db.commit()
    return db_todo
          
# Get Complete todo
@app.get("/todos/completed", response_model=List[Todo])
def get_completed_todo(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.owner_id==current_user.id, models.Todo.completed == True).all()
    return db_todo

# Get Pending todo
@app.get("/todos/pending", response_model=List[Todo])
def get_pending_todos(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.owner_id == current_user.id, models.Todo.completed == False).all()
    return db_todo

# Mark a todo complete

@app.patch("/todos/{todo_id}/toggle", response_model=TodoToggle)
def toggled(todo_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_todo = db.query(models.Todo).filter(models.Todo.owner_id==current_user.id, models.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail= "Todo not found")

    db_todo.completed = not db_todo.completed
            
    db.commit()
    db.refresh(db_todo)

    status = "completed" if db_todo.completed else "incomplete" 
    return {
        "message" : f" Todo {todo_id} has been marked {status}",
        "todo" : db_todo
        }
    

# Todo stats

@app.get("/stats")
def todo_stats(current_user:models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    total = db.query(models.Todo).filter(models.Todo.owner.id==current_user.id).count()
    completed = db.query(models.Todo).filter(models.Todo.owner_id==current_user.id, models.Todo.completed==True).count()
    pending = total - completed
    return {
        "total_todos": total,
        "completed": completed,
        "pending": pending,
        "percentage": f"{(completed/total*100):.1f}%" if total > 0 else "0%"
        }

