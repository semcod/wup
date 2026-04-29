from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_payments():
    return [{"id": 1, "amount": 100.0}, {"id": 2, "amount": 50.0}]


@router.get("/{payment_id}")
async def get_payment(payment_id: int):
    return {"id": payment_id, "amount": 100.0}


@router.post("/")
async def create_payment():
    return {"message": "Payment created"}
