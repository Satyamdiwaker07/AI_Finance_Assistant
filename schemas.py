from datetime import date
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class TransactionCreate(BaseModel):
    date: date
    description: str = Field(min_length=1, max_length=500)
    amount: float = Field(gt=0)
    type: Literal["income", "expense"]
    category: Optional[str] = Field(default=None, max_length=50)

class TransactionOut(BaseModel):
    id: int
    date: date
    description: str
    amount: float
    type: str
    category: str
    predicted_category: Optional[str] = None
    confidence: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)

class BudgetCreate(BaseModel):
    month: str = Field(pattern=r"^\d{4}-\d{2}$")
    category: str = Field(default="Overall", min_length=1, max_length=50)
    limit_amount: float = Field(gt=0)

class BudgetOut(BaseModel):
    id: int
    month: str
    category: str
    limit_amount: float
    spent: float
    usage_percent: float
    model_config = ConfigDict(from_attributes=True)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
