from fastapi import FastAPI
from Routes.CartRoutes import cart_router
from Routes.CategoryRoutes import category_router
from Routes.OrderRoutes import order_router
from Routes.ProductRoutes import product_router
from Routes.ReviewRoutes import review_router
from Routes.UserRoutes import user_router

app = FastAPI()
# uvicorn main:app --reload

app.include_router(cart_router, prefix="/carts", tags=["Carts"])
app.include_router(category_router, prefix="/categories", tags=["Categories"])
app.include_router(order_router, prefix="/orders", tags={"Orders"})
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(review_router, prefix="/reviews", tags=["Reviews"])
app.include_router(user_router, prefix="/users", tags=["Users"])

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do QXD E-commerce!"}