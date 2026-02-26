"""
Admin API endpoints.
"""

import uuid
from fastapi import APIRouter, HTTPException

from server.app.dependencies import DBSession, AdminUser
from server.app.services.user_service import list_users, update_user_role, deactivate_user
from server.app.schemas.user import UserAdminUpdateRequest, UserListResponse
from server.app.schemas.auth import UserResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=UserListResponse)
async def admin_list_users(
    admin: AdminUser, db: DBSession, page: int = 1, per_page: int = 20
):
    """List all users (admin only)."""
    users, total = await list_users(db, page, per_page)
    return UserListResponse(
        users=[
            UserResponse(
                id=str(u.id),
                email=u.email,
                full_name=u.full_name,
                role=u.role.value,
                is_active=u.is_active,
                created_at=u.created_at.isoformat(),
            )
            for u in users
        ],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/users/{user_id}/role")
async def admin_update_role(
    user_id: str,
    request: UserAdminUpdateRequest,
    admin: AdminUser,
    db: DBSession,
):
    """Update a user's role (admin only)."""
    try:
        user = await update_user_role(db, uuid.UUID(user_id), request.role)
        return {"status": "updated", "user_id": str(user.id), "role": user.role.value}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/users/{user_id}/deactivate")
async def admin_deactivate(
    user_id: str, admin: AdminUser, db: DBSession,
):
    """Deactivate a user account (admin only)."""
    try:
        user = await deactivate_user(db, uuid.UUID(user_id))
        return {"status": "deactivated", "user_id": str(user.id)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
