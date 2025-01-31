from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Product import Product

product_router = APIRouter()

@product_router.post("/", response_model=Product)
async def create_product(product: Product):
    product_dict = product.model_dump(exclude={'id'})
    new_product = await db.products.insert_one(product_dict)
    created_product = await db.products.find_one({"_id": new_product.inserted_id})
    
    if not created_product:
        raise HTTPException(status_code=400, detail="Erro ao criar produto")
    
    created_product['_id'] = str(created_product['_id'])
    
    return created_product