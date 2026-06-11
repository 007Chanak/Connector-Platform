from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas.auth import SignupRequest
from app.models.tenant import Tenant
from app.models.user import User
from app.utils.helpers import hash_password

from app.schemas.auth import LoginRequest
from app.utils.helpers import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
import jwt
from sqlalchemy import text
import bcrypt

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup")
def signup(
    data: SignupRequest,
    db: Session = Depends(get_db)
):

    existing_tenant = db.query(
        Tenant
    ).filter(
        Tenant.company_name.ilike(
            data.company_name
        )
    ).first()

    if existing_tenant:

        tenant = existing_tenant

    else:

        tenant = Tenant(
            company_name=data.company_name
        )

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    existing_user = db.query(
        User
    ).filter(
        User.email == data.email
    ).first()

    if existing_user:

        return {
            "error": "Email already exists"
        }

    user = User(
        email=data.email,
        password=hash_password(
            data.password
        ),
        tenant_id=tenant.id
    )

    db.add(user)
    db.commit()

    return {
        "message": "User created successfully",
        "tenant_id": tenant.id
    }


SECRET_KEY = "mysecretkey"

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    db = SessionLocal()

    try:

        user = db.execute(
            text("""
                SELECT *
                FROM users
                WHERE email = :email
            """),
            {
                "email": form_data.username
            }
        ).fetchone()

        if not user:

            raise HTTPException(
                status_code=401,
                detail="Invalid email"
            )

        if not bcrypt.checkpw(
            form_data.password.encode(),
            user.password.encode()
        ):

            raise HTTPException(
                status_code=401,
                detail="Invalid password"
            )

        token = jwt.encode(
            {
                "user_id": user.id
            },
            SECRET_KEY,
            algorithm="HS256"
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    finally:

        db.close()