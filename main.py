from database import Database
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


# you get the token with oauth2 scheme
# you get the username and password from OAuth2PasswordRequestForm which get the data
# from /token route

#jwt encode to encode the data with a sub which contains the data you want to keep for
# other routes

#jwt decode for reading the actual data.

#don't need passlib just use Postgres builtin SHA256 encryption to hash passwords


@app.post('/signup')
def signup(new_user: User):
    db = Database()
    db.exec("INSERT INTO users(username, password) VALUES (%s, sha256(%s))",(new_user.username, new_user.password))
    return new_user

async def get_current_username(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return username



# create the jwt token and returns it.
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@app.post("/token", response_model=Token)

async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):

    
    db = Database()
    user_auth_success : bool = db.exec("SELECT EXISTS(SELECT 1 FROM users WHERE username=%s AND password=sha256(%s))",
    (form_data.username, form_data.password))[0][0]

    
    if not user_auth_success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    #data refers to what you want to put in the token that you can 
    #retrieve in other routes that require auth.
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/users/me/")
async def read_users_me(username: str = Depends(get_current_username)):
    return {"username": username}

