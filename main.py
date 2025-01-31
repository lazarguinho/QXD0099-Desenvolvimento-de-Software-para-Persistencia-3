from fastapi import FastAPI
from Routes.UserRoutes import user_router
from Routes.CategoryRoutes import category_router
from Routes.ProductRoutes import product_router
from Routes.OrderRoutes import order_router

app = FastAPI()
# uvicorn main:app --reload

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(order_router, prefix="/orders", tags={"Orders"})

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do QXD E-commerce!"}