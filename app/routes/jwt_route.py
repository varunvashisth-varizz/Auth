from fastapi import APIRouter ,Depends , HTTPException , FastAPI
from typing import Annotated
import jwt
from ..services.authenticate_service import create_jwt_token
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm



router = APIRouter(prefix="/login")

@router.post("/jwt")
def jwt_authenticate(form_data : OAuth2PasswordRequestForm = Depends()):


    user = services.authenticate_service.validate_user(form_data.username , form_data.password)
    
    if user is None : 
        raise HTTPException(status_code=401, detail="Invalid Credentials")

    token = create_jwt_token(user.id)

    return {
        "access_token" : token ,
        "token_type" : "Bearer"
    }


@router.post("/session")
def session_login():
    ...

@router.get("/google")
def google_login():
    ...