from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.User import User


user_router = APIRouter()

@user_router.post("/", response_model=User)
async def create_user(user: User):
	user_dict = user.model_dump(exclude={'id'}, exclude_unset=True)
	new_user = await db.users.insert_one(user_dict)
	created_user = await db.users.find_one({"_id": new_user.inserted_id})

	if not created_user:
		raise HTTPException(status_code=400, detail="Erro ao criar usuário")

	created_user['_id'] = str(created_user['_id'])

	return created_user
