from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.User import User
from typing import List
from bson import ObjectId

user_router = APIRouter()

@user_router.get("/", response_model=List[User])
async def get_users(skip: int = 0, limit: int = 10):
    users = await db.users.find().skip(skip).limit(limit).to_list(100)

    for user in users:
        user['_id'] = str(user['_id'])

    return users

@user_router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    filt = {"_id": ObjectId(user_id)} if ObjectId.is_valid(user_id) else {"_id": user_id}

    user = await db.users.find_one(filt)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user['_id'] = str(user['_id'])

    return user

@user_router.post("/", response_model=User)
async def create_user(user: User):
    user_dict = user.model_dump(by_alias=True, exclude={'id'}, exclude_unset=True)

    new_user = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": new_user.inserted_id})

    if not created_user:
        raise HTTPException(status_code=400, detail="Erro ao criar usuário")

    created_user['_id'] = str(created_user['_id'])

    return created_user

@user_router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user_dict = user.model_dump(by_alias=True, exclude={'id'}, exclude_unset=True)

    result = await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user_dict})

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = await db.users.find_one({"_id": ObjectId(user_id)})

    if not updated_user:
        raise HTTPException(status_code=400, detail="Erro ao atualizar usuário")

    updated_user['_id'] = str(updated_user['_id'])

    return updated_user

@user_router.delete("/{user_id}")
async def delete_user(user_id: str):
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user_object_id = ObjectId(user_id)

    user = await db.users.find_one({"_id": user_object_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.users.delete_one({"_id": user_object_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Delete failed")

    return {"message": "User deleted successfully"}
