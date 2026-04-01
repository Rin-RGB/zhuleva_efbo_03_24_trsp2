from pydantic import BaseModel, Field, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int | None = Field(None, gt=0)
    is_subscribed: bool | None = None