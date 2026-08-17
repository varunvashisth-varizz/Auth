import jwt 
from ..db_models.user import user
from pwdlib import PasswordHash
from datetime import datetime , timezone , timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/jwt")


password_hashhed = PasswordHash.recommended()

def fetch_user_by_id(user_id : int , db):

    existing_user = (db.query(user).filter(user.id  == user_id).first())

    if not existing_user : 
        return None
    
def validate_user(username:str , password : str , db):

    existing_user = (db.query(user).filter(user.username == username).first())

    if not existing_user : 
        return None
    
    if not verify_password(password , existing_user.password_hash): 
        return None

    return existing_user 


def verify_password(password: str , password_hash : str) :

    verified = password_hash.verify(password_hash , password)

    return verified


def create_jwt_token(user_id : int , expire_min : int) : 

    payload = {
        "id" : user_id,
        "iat" : datetime.now(timezone.utc), 
        "exp" : datetime.now(timezone.utc) + timedelta(minutes = expire_min)
    }
    
    return jwt.encode( payload , SECRET_KEY , algorithm=ALGORITHM )


def get_current_user(token : str  = Depends(oauth2_scheme)) : 
    payload = jwt.decode(token , SECRET_KEY , algorithms=[ALGORITHM])
    user_id = payload.get("id")

    current_user = fetch_user_by_id(user_id)

    return current_user
