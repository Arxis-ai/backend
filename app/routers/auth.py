from fastapi import APIRouter, Depends

from app.services.supabase_client import require_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me")
async def get_me(user=Depends(require_current_user)):
    return {
        "id": user.id,
        "email": user.email,
    }
