from fastapi import Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User


def require_role(*allowed_roles):
    """Allow access only when the authenticated user's role matches."""

    def role_checker(
        current_user: User = Depends(get_current_user)
    ):
        user_role = str(current_user.role)

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "error": "Permission denied",
                    "user_role": user_role,
                    "allowed_roles": list(allowed_roles)
                }
            )

        return current_user

    return role_checker
