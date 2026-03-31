import sqlite3
import os
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# -------------------- CONFIG --------------------
SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-secret-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

# -------------------- HELPERS --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["auth"])


# -------------------- DATABASE SETUP --------------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# Run on import
init_db()


# -------------------- JWT UTILS --------------------
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# -------------------- SCHEMAS --------------------
class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# -------------------- DEPENDENCY --------------------
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    payload = decode_token(credentials.credentials)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    conn = get_db()
    row = conn.execute("SELECT id, name, email FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {"id": row["id"], "name": row["name"], "email": row["email"]}


# -------------------- ROUTES --------------------
@router.post("/register", response_model=AuthResponse)
def register(body: RegisterRequest):
    if not body.name.strip():
        raise HTTPException(status_code=422, detail="Name is required")
    if not body.email.strip():
        raise HTTPException(status_code=422, detail="Email is required")
    if len(body.password) < 6:
        raise HTTPException(status_code=422, detail="Password must be at least 6 characters")

    conn = get_db()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (body.email.lower(),)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed = pwd_context.hash(body.password)
    conn.execute(
        "INSERT INTO users (name, email, hashed_password, created_at) VALUES (?, ?, ?, ?)",
        (body.name.strip(), body.email.lower().strip(), hashed, datetime.utcnow().isoformat())
    )
    conn.commit()

    row = conn.execute("SELECT id, name, email FROM users WHERE email = ?", (body.email.lower(),)).fetchone()
    conn.close()

    user = {"id": row["id"], "name": row["name"], "email": row["email"]}
    token = create_access_token({"sub": user["email"]})
    return AuthResponse(access_token=token, user=user)


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest):
    conn = get_db()
    row = conn.execute(
        "SELECT id, name, email, hashed_password FROM users WHERE email = ?",
        (body.email.lower().strip(),)
    ).fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not pwd_context.verify(body.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user = {"id": row["id"], "name": row["name"], "email": row["email"]}
    token = create_access_token({"sub": user["email"]})
    return AuthResponse(access_token=token, user=user)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return current_user
