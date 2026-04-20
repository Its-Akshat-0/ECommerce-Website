from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleLogin(BaseModel):
    token: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    
    class Config:
        from_attributes = True
