from pydantic import BaseModel, EmailStr, Field

MAX_ID = 2**31 - 1

class Student(BaseModel):
    id: int | None = Field(None, gt=0,le=MAX_ID)
    name: str = Field(..., min_length=1,max_length=100)
    age: int = Field(..., gt=0,le=200)
    email: EmailStr = Field(...,max_length=100)
