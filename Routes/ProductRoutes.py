from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Product import Product
from typing import List
from bson import ObjectId

product_router = APIRouter()

@product_router.get("/", response_model=List[Product])
async def get_products(skip: int = 0, limit: int = 10):
    products = await db.products.find().skip(skip).limit(limit).to_list(100)

    for product in products:
        product['_id'] = str(product['_id'])

        if "carts" in product and isinstance(product["carts"], list):
            product["carts"] = [str(cart_id) if isinstance(cart_id, ObjectId) else cart_id for cart_id in product["carts"]]

    return products

@product_router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    filt = {"_id": ObjectId(product_id)} if ObjectId.is_valid(product_id) else {"_id": product_id}

    product = await db.products.find_one(filt)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product['_id'] = str(product['_id'])

    if "carts" in product and isinstance(product["carts"], list):
        product["carts"] = [str(cart_id) if isinstance(cart_id, ObjectId) else cart_id for cart_id in product["carts"]]

    return product

@product_router.post("/", response_model=Product)
async def create_product(product: Product):
    product_dict = product.model_dump(by_alias=True, exclude={'id'})

    new_product = await db.products.insert_one(product_dict)
    created_product = await db.products.find_one({"_id": new_product.inserted_id})

    if not created_product:
        raise HTTPException(status_code=400, detail="Erro ao criar produto")
    
    product_id_str = str(created_product['_id'])

    # Se houver carrinhos associados, adicionar o ID do produto à lista de produtos de cada carrinho
    if "carts" in product_dict and isinstance(product_dict["carts"], list):
        await db.carts.update_many(
            {"_id": {"$in": [ObjectId(cart_id) for cart_id in product_dict["carts"]]}},
            {"$addToSet": {"products": product_id_str}}
        )

    # Se houver pedidos associado, adicionar o ID do produto à lista de produtos de cada pedido
    if "orders" in product_dict and isinstance(product_dict["orders"], list):
        await db.orders.update_many(
            {"_id": {"$in": [ObjectId(order_id) for order_id in product_dict["orders"]]}},
            {"$addToSet": {"products": product_id_str}}
        )

    # Se houver uma categoria associada, adicionar o ID da categoria à lista de categorias de cada produto
    if "category_id" in product_dict and product_dict["category_id"]:
        await db.categories.update_one(
            {"_id": ObjectId(product_dict["category_id"])},
            {"$addToSet": {"products": product_id_str}}
        )

    created_product['_id'] = product_id_str

    return created_product

@product_router.put("/{product_id}", response_model=Product)
async def update_product(product_id: str, product: Product):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product_dict = product.model_dump(by_alias=True, exclude={'id'})

    result = await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": product_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    updated_product = await db.products.find_one({"_id": ObjectId(product_id)})

    if not updated_product:
        raise HTTPException(status_code=400, detail="Erro ao atualizar produto")

    product_id_str = str(updated_product['_id'])

    if "carts" in product_dict and isinstance(product_dict["carts"], list):
        await db.carts.update_many(
            {"_id": {"$in": [ObjectId(cart_id) for cart_id in product_dict["carts"]]}},
            {"$addToSet": {"products": product_id_str}}
        )

    if "orders" in product_dict and isinstance(product_dict["orders"], list):
        await db.orders.update_many(
            {"_id": {"$in": [ObjectId(order_id) for order_id in product_dict["orders"]]}},
            {"$addToSet": {"products": product_id_str}}
        )

    if "category_id" in product_dict and product_dict["category_id"]:
        await db.categories.update_one(
            {"_id": ObjectId(product_dict["category_id"])},
            {"$addToSet": {"products": product_id_str}}
        )

    updated_product['_id'] = product_id_str

    

    return updated_product

@product_router.delete("/{product_id}")
async def delete_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    product_object_id = ObjectId(product_id)

    product = await db.products.find_one({"_id": product_object_id})

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = await db.products.delete_one({"_id": product_object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delete failed")

    await db.carts.update_many(
        {"products": product_object_id},
        {"$pull": {"products": product_object_id}}
    )

    await db.orders.update_many(
        {"products": product_object_id},
        {"$pull": {"products": product_object_id}}
    )

    await db.categories.update_many(
        {"products": product_object_id},
        {"$pull": {"products": product_object_id}}
    )

    return {"message": "Product deleted successfully"}

@product_router.get("/count")
async def get_product_count():    
    count = await db.products.count_documents({})
    return {"total_products": count}
