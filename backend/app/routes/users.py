from fastapi import APIRouter, Depends, HTTPException

from app.auth.permissions import require_role
from app.logger import logger
from app.schemas.user import UserRoleUpdate, UserStatusUpdate
from app.services.user_service import user_service

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ------------------------------------
# Get All Users
# ------------------------------------
@router.get("/")
async def get_all_users(
    current_user=Depends(require_role("ADMIN"))
):
    try:

        users = user_service.get_all_users()

        return {
            "success": True,
            "count": len(users),
            "users": users
        }

    except Exception as e:

        logger.exception("Failed to fetch users.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ------------------------------------
# Get User By ID
# ------------------------------------
@router.get("/{user_id}")
async def get_user(
    user_id: str,
    current_user=Depends(require_role("ADMIN"))
):
    try:

        return user_service.get_user(user_id)

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Failed to fetch user.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ------------------------------------
# Update User Role
# ------------------------------------
@router.put("/{user_id}/role")
async def update_role(
    user_id: str,
    request: UserRoleUpdate,
    current_user=Depends(require_role("ADMIN"))
):
    try:

        return user_service.update_role(
            current_user=current_user,
            user_id=user_id,
            role=request.role
        )

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Failed to update role.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ------------------------------------
# Enable / Disable User
# ------------------------------------
@router.put("/{user_id}/status")
async def update_status(
    user_id: str,
    request: UserStatusUpdate,
    current_user=Depends(require_role("ADMIN"))
):
    try:

        return user_service.update_status(
            current_user=current_user,
            user_id=user_id,
            enabled=request.enabled
        )

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Failed to update user status.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ------------------------------------
# Delete User
# ------------------------------------
@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user=Depends(require_role("ADMIN"))
):
    try:

        return user_service.delete_user(
            current_user=current_user,
            user_id=user_id
        )

    except HTTPException:
        raise

    except Exception as e:

        logger.exception("Failed to delete user.")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )