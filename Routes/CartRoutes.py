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

    return carts

@cart_router.get("/{cart_id}", response_model=Cart)
async def get_cart(cart_id: str):
    filt = {"_id": ObjectId(cart_id)} if ObjectId.is_valid(cart_id) else {"_id": cart_id}

    cart = await db.carts.find_one(filt)

    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    cart['_id'] = str(cart['_id'])

    return cart

@cart_router.post("/", response_model=Cart)
async def create_cart(cart: Cart):
    cart_dict = cart.model_dump(by_alias=True, exclude={'id'})
    
    new_cart = await db.carts.insert_one(cart_dict)

    created_cart = await db.carts.find_one({"_id": new_cart.inserted_id})

    if not created_cart:
        raise HTTPException(status_code=400, detail="Erro ao criar carrinho")

    created_cart['_id'] = str(created_cart['_id'])

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

    updated_cart['_id'] = str(updated_cart['_id'])

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

    return {"message": "Cart deleted successfully"}