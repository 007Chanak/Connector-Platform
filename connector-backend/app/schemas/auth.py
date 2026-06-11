from pydantic import BaseModel

class SignupRequest(BaseModel):
    company_name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str