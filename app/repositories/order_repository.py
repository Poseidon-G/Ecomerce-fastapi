from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.model import Order
from app.repositories.base_repository import BaseRepository

class OrderRepository(BaseRepository[Order]):
    def __init__(self, db: Session):
        super().__init__(db)
