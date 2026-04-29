from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class User(BaseModel):
    id: int
    name: str
    email: str


@router.get("/")
async def list_users():
    return [
        {"id": 1, "name": "John Doe", "email": "john@example.com"},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
    ]


@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "John Doe", "email": "john@example.com"}


@router.post("/")
async def create_user(user: User):
    return {"message": "User created", "user": user}


@router.put("/{user_id}")
async def update_user(user_id: int, user: User):
    return {"message": "User updated", "user_id": user_id, "user": user}


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    return {"message": "User deleted", "user_id": user_id}
