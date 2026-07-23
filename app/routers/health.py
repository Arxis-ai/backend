from fastapi import APIRouter, HTTPException, status

from app.services.supabase_client import check_db_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/health/db")
async def db_health():
    try:
        result = await check_db_connection()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database health check failed",
        ) from exc

    return {
        "status": "ok",
        "database": result,
    }
