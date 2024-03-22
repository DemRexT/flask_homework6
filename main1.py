import databases 
from fastapi import FastAPI
from typing import List
import sqlalchemy 
from pydantic import BaseModel, Field, EmailStr
from datetime import date

DATABASE_URL = 'sqlite:///homework6/dbusers.db'
database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(80)),
    sqlalchemy.Column('last_name', sqlalchemy.String(120)),
    sqlalchemy.Column('date_of_birth', sqlalchemy.DateTime),
    sqlalchemy.Column('email', sqlalchemy.String(80)),
    sqlalchemy.Column('address', sqlalchemy.String(200))
)


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={'check_same_thread': False}
)
metadata.create_all(engine)


app = FastAPI()

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    date_of_birth: date
    address: str = Field(min_length=5)
    class Config:
        json_encoders = {
            date: lambda v: v.strftime('%Y-%m-%d')
        }


class UserNotId(BaseModel):
    name: str = Field(..., min_length=2)
    last_name: str = Field(..., min_length=2)
    date_of_birth: date
    email: EmailStr
    address: str = Field(min_length=5)
    class Config:
        json_encoders = {
            date: lambda v: v.strftime('%Y-%m-%d')
        }



@app.post('/users/', response_model=User)
async def add_user(user: UserNotId):
    query = users.insert().values(**user.dict())
    await database.execute(query)

@app.get('/users/', response_model= List[User])
async def get_users():
    query = users.select()
    return await database.fetch_all(query)


@app.get('/users/{id}', response_model= User)
async def get_user(id: int):
    query = users.select().where(users.c.id == id)
    return await database.fetch_one(query)


@app.put('/users/{id}', response_model= User)
async def put_user(id: int, user: UserNotId):
    query = users.update().where(users.c.id == id).values(**user.dict())
    await database.execute(query)


@app.delete('/users/{id}')
async def del_user(id: int):
    query = users.delete().where(users.c.id == id)
    await database.execute(query)