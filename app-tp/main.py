from fastapi import FastAPI, Depends, HTTPException, Request, Form
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import crud,models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

#Dependency
def get_db():
    db = SessionLocal()
    try : 
        yield db
    finally:
        db.close()

app.mount("/static", StaticFiles(directory="public"), name="public")

templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request, "home.html")

@app.get('/basic')
def get_basic_form(request: Request):
    return templates.TemplateResponse("users_create.html", {"request": request})

@app.post('/basic')
async def post_basic_form(request: Request, formusername: str = Form(...), 
formemail: str = Form(...),db:Session=Depends(get_db)):
    print(f'username: {formusername}')
    print(f'email: {formemail}')
    db_user = crud.get_user_by_email(db, email=formemail)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = models.user(name=formusername,email=formemail)

    return crud.create_user(db=db,user=user)

    


@app.post("/users/",response_model=schemas.User)
def post_user(user:schemas.UserCreate, db:Session=Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db,user=user)


@app.get("/users/", response_model=list[schemas.User])
def get_users(skip:int=0, limit:int=0, db:Session=Depends(get_db)):
    users = crud.get_users(db,skip=skip,limit=limit)
    return users


@app.get("/users/{user_id}/",response_model=schemas.User)
def get_user(user_id:int, db:Session=Depends(get_db)):
    db_user = crud.get_user(db,user_id =user_id )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/todos/",response_model=schemas.Todo)
def post_todo_for_user(user_id:int, todo:schemas.TodoCreate, db:Session=Depends(get_db)):
    return crud.create_user_todo(db=db,user_id=user_id, todo=todo)


@app.get("/todos/", response_model=list[schemas.Todo])
def get_todos(skip:int=0,limit:int=100,db:Session=Depends(get_db)):
    todos = crud.get_todos(db,skip=skip,limit=limit)
    return todos