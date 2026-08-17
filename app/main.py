from fastapi import FastAPI 
from routes import jwt_route

app = FastAPI()

app.include_router(jwt_route.router)

@app.on_event("startup")