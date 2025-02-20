from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Cart import Cart
from typing import List
from bson import ObjectId

cart_router = APIRouter()

@cart_router.get("/", response_model=List[Cart])
async def get_carts(skip: int = 0, limit: int = 10):
    carts = await db.carts.find().skip(skip).limit(limit).to_list(100)

    for cart in carts:
        cart['_id'] = str(cart['_id'])

        if "produts" in cart and isinstance(cart["products"], list):
            cart["products"] = [str(product_id) if isinstance(product_id, ObjectId) else product_id for product_id in cart["products"]]

    return carts

@cart_router.get("/{cart_id}", response_model=Cart)
async def get_cart(cart_id: str):
    filt = {"_id": ObjectId(cart_id)} if ObjectId.is_valid(cart_id) else {"_id": cart_id}

    cart = await db.carts.find_one(filt)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart['_id'] = str(cart['_id'])

    if "produts" in cart and isinstance(cart["products"], list):
        cart["products"] = [str(product_id) if isinstance(product_id, ObjectId) else product_id for product_id in cart["products"]]

    return cart

@cart_router.post("/", response_model=Cart)
async def create_cart(cart: Cart):
    cart_dict = cart.model_dump(by_alias=True, exclude={'id'})

    new_cart = await db.carts.insert_one(cart_dict)
    created_cart = await db.carts.find_one({"_id": new_cart.inserted_id})

    if not created_cart:
        raise HTTPException(status_code=400, detail="Erro ao criar carrinho")

    cart_id_str = str(created_cart['_id'])

    # Se houver um usuário associado, atualizar o ID do carrinho na coleção de usuários
    if "user_id" in cart_dict and cart_dict["user_id"]:
        await db.users.update_one(
            {"_id": ObjectId(cart_dict["user_id"])},
            {"$set": {"carrinho_id": cart_id_str}}
        )

    # Se houver produtos no carrinho, adicionar o ID do carrinho à lista de carrinhos de cada produto
    if "products" in cart_dict and isinstance(cart_dict["products"], list):
        await db.products.update_many(
            {"_id": {"$in": [ObjectId(product_id) for product_id in cart_dict["products"]]}},
            {"$addToSet": {"carts": cart_id_str}}
        )

    created_cart['_id'] = cart_id_str

    return created_cart


@cart_router.put("/{cart_id}", response_model=Cart)
async def update_cart(cart_id: str, cart: Cart):
    if not ObjectId.is_valid(cart_id):
        raise HTTPException(status_code=400, detail="Invalid cart ID")
    
    cart_dict = cart.model_dump(by_alias=True, exclude={'id'})

    result = await db.carts.update_one({"_id": ObjectId(cart_id)}, {"$set": cart_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Cart not found")

    updated_cart = await db.carts.find_one({"_id": ObjectId(cart_id)})

    if not updated_cart:
        raise HTTPException(status_code=400, detail="Erro ao atualizar carrinho")

    cart_id_str = str(updated_cart['_id'])

    # Se houver um usuário associado, atualizar o ID do carrinho na coleção de usuários
    if "user_id" in cart_dict and cart_dict["user_id"]:
        await db.users.update_one(
            {"_id": ObjectId(cart_dict["user_id"])},
            {"$set": {"carrinho_id": cart_id_str}}
        )

    # Se houver produtos no carrinho, adicionar o ID do carrinho à lista de carrinhos de cada produto
    if "products" in cart_dict and isinstance(cart_dict["products"], list):
        await db.products.update_many(
            {"_id": {"$in": [ObjectId(product_id) for product_id in cart_dict["products"]]}},
            {"$addToSet": {"carts": cart_id_str}}
        )

    updated_cart['_id'] = cart_id_str

    return updated_cart


@cart_router.delete("/{cart_id}")
async def delete_cart(cart_id: str):
    if not ObjectId.is_valid(cart_id):
        raise HTTPException(status_code=400, detail="Invalid cart ID")

    cart_object_id = ObjectId(cart_id)

    cart = await db.carts.find_one({"_id": cart_object_id})

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
       
    result = await db.carts.delete_one({"_id": cart_object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delete failed")
    
    await db.products.update_many(
        {"carts": cart_object_id},
        {"$pull": {"carts": cart_object_id}}
    )

    await db.users.update_one(
        {"carrinho_id": cart_object_id},
        {"$unset": {"carrinho_id": ""}}
    )

    return {"message": "Cart deleted successfully"}

@cart_router.get("/user/{user_id}", response_model=List[Cart])
async def get_carts_by_user(user_id: str):
    filt = {"user_id": user_id}

    carts = await db.carts.find(filt).to_list(100)

    for cart in carts:
        cart['_id'] = str(cart['_id'])

        if "produts" in cart and isinstance(cart["products"], list):
            cart["products"] = [str(product_id) if isinstance(product_id, ObjectId) else product_id for product_id in cart["products"]]

    return carts

@cart_router.put("/user/{user_id}", response_model=List[Cart])
async def link_user_to_cart(user_id: str, cart_id: str):
    filt = {"_id": ObjectId(cart_id)} if ObjectId.is_valid(cart_id) else {"_id": cart_id}

    cart = await db.carts.find_one(filt)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart['_id'] = str(cart['_id'])

    if "produts" in cart and isinstance(cart["products"], list):
        cart["products"] = [str(product_id) if isinstance(product_id, ObjectId) else product_id for product_id in cart["products"]]

    result = await db.carts.update_one({"_id": ObjectId(cart_id)}, {"$set": {"user_id": user_id}})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Cart not found")

    return await get_carts_by_user(user_id)

@cart_router.delete("/user/{user_id}")
async def unlink_user_cart(user_id: str):
    result = await db.carts.update_many({"user_id": user_id}, {"$unset": {"user_id": ""}})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Cart not found")

    return {"message": "User cart unlinked successfully"}

@cart_router.get("/count")
async def get_cart_count():
    count = await db.carts.count_documents({})
    return {"total_carts": count}
