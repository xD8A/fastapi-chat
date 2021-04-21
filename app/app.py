from typing import Union, List
from collections import defaultdict
from sqlalchemy.orm import Session
from fastapi import FastAPI, WebSocket, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from .database import engine, Base
from . import models, schemas


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')
Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

all_chat_websockets = defaultdict(list)     # should be thread safe by GIL (factory is list)


def get_db():
    from .database import SessionLocal

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user_id_by_token(token: str = Depends(oauth2_scheme)) -> int:
    from .schemas.users import UserSignedIn

    try:
        user_id = UserSignedIn.get_user_id(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user_id


@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})


@app.post('/sign-in', response_model=schemas.UserSignedIn)
def sign_in(user: Union[schemas.UserSignIn, schemas.UserSignInByName], db: Session = Depends(get_db)):
    name = getattr(user, 'name', None)
    email = getattr(user, 'email', None)
    cond = (models.User.email == email) if name is None else (models.User.name == name)
    db_user = db.query(models.User).filter(cond).one_or_none()
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return db_user


@app.get('/users', response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    db_users = db.query(models.User).offset(skip).limit(limit).all()
    return db_users


@app.get('/contacts', response_model=List[schemas.Contact])
def read_user_contacts(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id_by_token)):
    db_contacts = db.query(models.Contact).filter(models.Contact.owner_id == user_id).all()
    return db_contacts


@app.post('/contacts', response_model=schemas.Contact)
def add_user_contact(contact: schemas.ContactAdd,
                     db: Session = Depends(get_db),
                     user_id: int = Depends(get_current_user_id_by_token)):
    friend_id = contact.friend.id
    db_friend = db.query(models.User).filter(models.User.id == friend_id).one_or_none()
    if db_friend is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    contact_name = getattr(contact, 'name', db_friend.name)
    db_contact = models.Contact(owner_id=user_id, friend_id=friend_id, name=contact_name)
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


@app.get('/contacts/{contact_id}/messages', response_model=List[schemas.Message])
def read_contact_messages(contact_id: int, skip: int = 0, limit: int = 100, asc: bool = False,
                          db: Session = Depends(get_db),
                          user_id: int = Depends(get_current_user_id_by_token)):
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).one_or_none()
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Contact not found')
    if db_contact.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Contact does not belong to you')
    order = models.Message.created_at.asc() if asc else models.Message.created_at.desc()
    messages = db.query(models.Message).join(models.Contact.messages).filter(models.Contact.id == contact_id)\
        .order_by(order).offset(skip).limit(limit).all()
    return messages


@app.websocket('/chat/{contact_id}')
async def websocket_endpoint(
        websocket: WebSocket,
        contact_id: int,
        token: str,
        db: Session = Depends(get_db)   # TODO: run_in_executor?
):
    user_id = get_current_user_id_by_token(token)

    # TODO: run_in_executor?
    db_contact = db.query(models.Contact).filter(models.Contact.id == contact_id).one_or_none()
    if db_contact is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Contact not found')
    if db_contact.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Contact does not belong to you')
    # TODO: run_in_executor?
    db_friend_contact = db.query(models.Contact).filter(models.Contact.owner_id == db_contact.friend_id,
                                                        models.Contact.friend_id == db_contact.owner_id).one_or_none()
    if db_friend_contact and db_friend_contact.id == db_contact.id:
        db_friend_contact = None

    chat_key = tuple(sorted((db_contact.friend_id, user_id)))
    all_chat_websockets[chat_key].append(websocket)

    await websocket.accept()
    while True:
        text = await websocket.receive_text()

        # TODO: run_in_executor?
        db_message = models.Message(author_id=user_id, text=text)
        db_contact.messages.append(db_message)
        db.add(db_contact)
        if db_friend_contact:
            db_friend_contact.messages.append(db_message)
            db.add(db_contact)
        db.commit()
        db.refresh(db_message)
        message = schemas.Message.from_orm(db_message)
        data = message.json(exclude={'id'})

        for chat_websocket in all_chat_websockets[chat_key]:
            await chat_websocket.send_text(data)
