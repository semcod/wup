from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_users():
    return [{"id": 1, "name": "John Doe"}, {"id": 2, "name": "Jane Smith"}]


@router.get("/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "John Doe"}


@router.post("/")
async def create_user():
    return {"message": "User created"}
