from typing import Any, Dict, List, Optional, Tuple
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.models.model import User
from sqlalchemy.orm import Session
from app.utils.auth import auth_utils


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
        self.auth_utils = auth_utils

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
            
        object_dump = user_data.model_dump()
        object_dump["password_hash"] = self.auth_utils.get_password_hash(user_data.password)
        object_dump["role"] = user_data.role.value
        #remove password from object_dump
        del object_dump["password"]

        print("object_dump", object_dump)
        return await self.repository.create(object_dump)

    async def get_users(
        self,
        page: int = 1,
        size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[User], int]:
        """Get all users."""
        skip = (page - 1) * size
        limit = size
        users, total = await self.repository.get_all(
            filters=filters,
            skip=skip,
            limit=limit
        ), await self.repository.count(filters=filters)

        return users, total

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user."""
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await self.repository.update(user, user_data.model_dump())

    async def delete_user(self, user_id: int) -> bool:
        """Deactivate user."""
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return await self.repository.delete(user)

    async def get_current_user(self) -> Optional[User]:
        """Get current user profile."""
        # This method will be implemented in the next section
        pass

    async def update_password(self, password_data: UserPasswordUpdate) -> bool:
        """Update user password."""
        user = await self.repository.get(password_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not password_data.new_password == password_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")

        if not user.check_password(password_data.old_password):
            raise HTTPException(status_code=400, detail="Invalid password")

        new_password_hash = self.auth_utils.get_password_hash(password_data.new_password)
        user.password_hash = new_password_hash
        return await self.repository.commit()
        

    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user."""
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = False
        return await self.repository.commit()
    
    async def activate_user(self, user_id: int) -> bool:
        """Activate user."""
        user = await self.repository.get(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.is_active = True
        return await self.repository.commit()
