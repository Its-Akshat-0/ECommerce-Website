from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database, auth
from datetime import timedelta
import urllib.parse
import json
import httpx

# Simple in-memory cache
from functools import lru_cache
product_cache = {}

def map_product(dummy_prod):
    return {
        "id": dummy_prod.get("id"),
        "title": dummy_prod.get("title", ""),
        "price": dummy_prod.get("price", 0),
        "description": dummy_prod.get("description", ""),
        "category": dummy_prod.get("category", ""),
        "image": dummy_prod.get("thumbnail", ""),
        "rating": {
            "rate": dummy_prod.get("rating", 0),
            "count": dummy_prod.get("stock", 0)
        }
    }

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"], # allow React local instances
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(email=user.email, name=user.name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model=schemas.Token)
def login(user_credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=403, detail="Invalid Credentials")
    
    if not auth.verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=403, detail="Invalid Credentials")
        
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "name": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/google-login", response_model=schemas.Token)
def google_login(google_login: schemas.GoogleLogin, db: Session = Depends(database.get_db)):
    idinfo = auth.verify_google_token(google_login.token)
    if not idinfo:
        raise HTTPException(status_code=400, detail="Invalid Google Token")
        
    email = idinfo.get("email")
    name = idinfo.get("name")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    
    # If user doesn't exist, register them implicitly
    if not user:
        user = models.User(email=email, name=name, hashed_password=None)
        db.add(user)
        db.commit()
        db.refresh(user)
        
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email, "name": user.name}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me", response_model=schemas.UserResponse)
def get_current_user_details(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

@app.get("/products")
def get_products():
    if "all" in product_cache:
        return product_cache["all"]
    try:
        with httpx.Client() as client:
            # We use dummyjson since fakestoreapi is down
            response = client.get("https://dummyjson.com/products?limit=100")
            response.raise_for_status()
            data = response.json().get("products", [])
            mapped_data = [map_product(p) for p in data]
            product_cache["all"] = mapped_data
            return mapped_data
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

@app.get("/products/{product_id}")
def get_product(product_id: str):
    # Try to find in 'all' cache first for max speed
    if "all" in product_cache:
        for p in product_cache["all"]:
            if str(p.get("id")) == str(product_id):
                return p
                
    
    cache_key = f"product_{product_id}"
    if cache_key in product_cache:
        return product_cache[cache_key]
    try:
        with httpx.Client() as client:
            response = client.get(f"https://dummyjson.com/products/{product_id}")
            response.raise_for_status()
            data = response.json()
            mapped = map_product(data)
            product_cache[cache_key] = mapped
            return mapped
    except Exception as e:
        print(f"Error fetching product: {e}")
        return {}

@app.get("/products/category/{category_name}")
def get_category_products(category_name: str):
    cache_key = f"category_{category_name}"
    if cache_key in product_cache:
        return product_cache[cache_key]
    # URL encode the category name specifically (like handle spaces)
    encoded_category = urllib.parse.quote(category_name)
    try:
        with httpx.Client() as client:
            response = client.get(f"https://dummyjson.com/products/category/{encoded_category}")
            response.raise_for_status()
            data = response.json().get("products", [])
            mapped_data = [map_product(p) for p in data]
            product_cache[cache_key] = mapped_data
            return mapped_data
    except Exception as e:
        print(f"Error fetching category: {e}")
        return []
