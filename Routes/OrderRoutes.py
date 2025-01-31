from fastapi import APIRouter, HTTPException
from Config.config import db
from Models.Order import Order

order_router = APIRouter()

@order_router.post("/", response_model=Order)
async def create_order(order: Order):
	order_dict = order.model_dump(exclude={'id'})
	new_user = await db.orders.insert_one(order_dict)
	created_order = await db.orders.find_one({"_id" : new_user.inserted_id})
 
	if not created_order:
		raise HTTPException(status_code=400, detail="Erro ao criar pedido")

	created_order['_id'] = str(created_order['_id'])

	return created_order