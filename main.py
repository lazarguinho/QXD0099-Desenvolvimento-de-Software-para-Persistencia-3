from fastapi import FastAPI
from Routes.UserRoutes import user_router

app = FastAPI()
# uvicorn main:app --reload

app.include_router(user_router, prefix="/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do QXD E-commerce!"}