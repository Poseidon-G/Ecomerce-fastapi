from typing import List, Optional
from fastapi import HTTPException
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserPasswordUpdate
from app.models.model import User
from sqlalchemy.orm import Session


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        return await self.repository.create(user_data.model_dump())

    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users."""
        return await self.repository.get_all(skip=skip, limit=limit)

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
        user.set_password(password_data.new_password)
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
