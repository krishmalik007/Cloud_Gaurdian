from fastapi import HTTPException, status

from app.services.audit_service import audit_service
from app.storage.user_repository import UserRepository


class UserService:

    def __init__(self):
        self.repository = UserRepository()

    # ------------------------------------
    # Get All Users
    # ------------------------------------
    def get_all_users(self):

        users = self.repository.get_all_users()

        for user in users:
            user.pop("password", None)

        return users

    # ------------------------------------
    # Get User By ID
    # ------------------------------------
    def get_user(self, user_id: str):

        user = self.repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        user.pop("password", None)

        return user

    # ------------------------------------
    # Update User Role
    # ------------------------------------
    def update_role(
        self,
        current_user: dict,
        user_id: str,
        role: str
    ):

        user = self.repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        self.repository.update_role(
            user_id=user_id,
            role=role
        )

        audit_service.create_log(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="UPDATE_ROLE",
            resource=user_id,
            status="SUCCESS"
        )

        return {
            "message": "User role updated successfully."
        }

    # ------------------------------------
    # Enable / Disable User
    # ------------------------------------
    def update_status(
        self,
        current_user: dict,
        user_id: str,
        enabled: bool
    ):

        user = self.repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        self.repository.update_status(
            user_id=user_id,
            enabled=enabled
        )

        audit_service.create_log(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="UPDATE_USER_STATUS",
            resource=user_id,
            status="SUCCESS"
        )

        return {
            "message": "User status updated successfully."
        }

    # ------------------------------------
    # Delete User
    # ------------------------------------
    def delete_user(
        self,
        current_user: dict,
        user_id: str
    ):

        user = self.repository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        self.repository.delete_user(user_id)

        audit_service.create_log(
            user_id=current_user["user_id"],
            username=current_user["username"],
            action="DELETE_USER",
            resource=user_id,
            status="SUCCESS"
        )

        return {
            "message": "User deleted successfully."
        }


user_service = UserService()