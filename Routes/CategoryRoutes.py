from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Category import Category

category_router = APIRouter()

@category_router.post("/", response_model=Category)
async def create_category(user: Category):
	category_dict = user.model_dump(exclude={'id'}, exclude_unset=True)
	new_category = await db.categories.insert_one(category_dict)
	created_category = await db.categories.find_one({"_id": new_category.inserted_id})

	if not created_category:
		raise HTTPException(status_code=400, detail="Erro ao criar usuário")

	created_category['_id'] = str(created_category['_id'])

	return created_category