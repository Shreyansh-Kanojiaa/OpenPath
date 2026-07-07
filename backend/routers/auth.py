from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

import models, database, schemas, auth as auth_lib
from limiter import limiter, LOGIN_RATE, REGISTER_RATE

router = APIRouter(tags=["auth"])


@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
@limiter.limit(REGISTER_RATE)
def register(request: Request, user_in: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """Register a new user. Returns a success message — client must redirect to login."""
    email_norm = user_in.email.strip().lower()
    username_norm = user_in.username.strip()

    if db.query(models.User).filter(models.User.email == email_norm).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    if db.query(models.User).filter(models.User.username == username_norm).first():
        raise HTTPException(status_code=400, detail="Username already taken.")

    new_user = models.User(
        username=username_norm,
        email=email_norm,
        hashed_password=auth_lib.hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Account created successfully. Please log in.", "username": new_user.username}


@router.post("/auth/login", response_model=schemas.Token)
@limiter.limit(LOGIN_RATE)
def login(request: Request, creds: schemas.UserLogin, db: Session = Depends(database.get_db)):
    """Login with email + password and return a JWT."""
    email_norm = creds.email.strip().lower()
    user = db.query(models.User).filter(models.User.email == email_norm).first()
    if not user or not user.hashed_password or not auth_lib.verify_password(creds.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = auth_lib.create_access_token({"sub": str(user.id)})
    return schemas.Token(access_token=token, user_id=user.id, username=user.username)


@router.get("/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: models.User = Depends(auth_lib.get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user
