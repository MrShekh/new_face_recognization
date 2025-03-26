from passlib.context import CryptContext
import jwt
from fastapi import HTTPException, Request, Response, Depends
from datetime import datetime, timedelta

# ✅ Password Hashing Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Hash Password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# ✅ Verify Password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ✅ JWT Configuration
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour expiration

# ✅ Generate JWT Token
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ✅ Decode JWT Token
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Returns user_id and role
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ✅ Set Token in Cookies (Use this in Login API)
def set_jwt_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,  # Prevents JavaScript access (More secure)
        samesite="Lax",  # Prevents CSRF attacks
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Expiry in seconds
    )

# ✅ Dependency: Get current user from cookies
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_data = verify_jwt_token(token)
    return user_data
