from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.model import User
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)