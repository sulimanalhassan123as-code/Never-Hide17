from pydantic import BaseModel

class UserCreate(BaseModel):
    phone: str
    password: str

class UserResponse(BaseModel):
    id: int
    phone: str
    wallet: float

    class Config:
        orm_mode = True
