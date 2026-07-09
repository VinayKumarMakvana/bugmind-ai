from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from app.db.session import get_db
from app.models.domain import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str
    name: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    has_openai_key: bool

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    openai_api_key: Optional[str] = None

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate, db = Depends(get_db)):
    user = await db.users.find_one({"email": user_in.email})
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=get_password_hash(user_in.password)
    )
    await db.users.insert_one(new_user.model_dump())
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        has_openai_key=bool(new_user.openai_api_key)
    )

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user = await db.users.find_one({"email": form_data.username})
    if not user or not user.get("password_hash") or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name or "",
        has_openai_key=bool(current_user.openai_api_key)
    )

@router.put("/me", response_model=UserResponse)
async def update_me(profile_in: UserProfileUpdate, db = Depends(get_db), current_user: User = Depends(get_current_user)):
    update_data = {}
    if profile_in.name is not None:
        update_data["name"] = profile_in.name
        current_user.name = profile_in.name
    if profile_in.openai_api_key is not None:
        update_data["openai_api_key"] = profile_in.openai_api_key
        current_user.openai_api_key = profile_in.openai_api_key

    if update_data:
        await db.users.update_one({"id": current_user.id}, {"$set": update_data})
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name or "",
        has_openai_key=bool(current_user.openai_api_key)
    )
