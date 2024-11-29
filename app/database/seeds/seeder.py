from typing import List
from datetime import datetime
from fastapi import Depends
from sqlalchemy.orm import Session
from app.utils.auth import auth_utils
from app.database.connection import get_db
from app.services.user_service import UserService
from app.services.category_service import CategoryService
from app.services.product_service import ProductService
from app.models.model import Category, User, UserRole
from app.schemas.category import CategoryCreate
from app.schemas.product import ProductCreate
from app.schemas.user import UserCreate

class Seeder:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.auth_utils = auth_utils
        self.category_service = CategoryService(db)
        self.product_service = ProductService(db)
        self.user_service = UserService(db)

    async def seed_users(self) -> List[User]:
        try:
            
            users = [
                UserCreate(email="admin@gmail.com", password="admin123", role="admin", first_name="Admin", last_name="User"),
                UserCreate(email="staff@gmail.com", password="staff123", role="staff", first_name="Staff", last_name="User"),
                UserCreate(email="customer@gmail.com", password="customer123", role="customer", first_name="Customer", last_name="User"),
            ]
            created_users = []

            for user in users:
                created_user = await self.user_service.create_user(user)
                created_users.append(created_user)
            return created_users

        except Exception as e:
            print(e)
            print(f"❌ Error seeding users: {str(e)}")
            return []

    async def seed_categories(self) -> List[Category]:
        try: 
            categories = [
                CategoryCreate(name="Electronics", description="Electronic gadgets"),
                CategoryCreate(name="Clothing", description="Fashionable clothes"),
                CategoryCreate(name="Books", description="Reading materials"),
                CategoryCreate(name="Furniture", description="Home and office furniture"),
                CategoryCreate(name="Food", description="Edible goods"),
            ]
            
            created_categories = []

            for category in categories:
                # Check if category already exists
                created_category = await self.category_service.create_category(category)
                created_categories.append(created_category)
            return created_categories
        except Exception as e:
            print(f"❌ Error seeding categories: {str(e)}")
            return []
        
    
    async def seed_products(self, categories: List[Category]):
        try:
            products = [
                ProductCreate(
                    name="Laptop",
                    description="A portable computer",
                    price=500.00,
                    stock=100,
                    category_id=categories[0].id
                ),
                ProductCreate(
                    name="T-shirt",
                    description="A casual wear",
                    price=20.00,
                    stock=200,
                    category_id=categories[1].id
                ),
                ProductCreate(
                    name="Python Crash Course",
                    description="A book for beginners",
                    price=30.00,
                    stock=50,
                    category_id=categories[2].id
                ),
                ProductCreate(
                    name="Office Chair",
                    description="A comfortable chair",
                    price=100.00,
                    stock=20,
                    category_id=categories[3].id
                ),
                ProductCreate(
                    name="Rice",
                    description="A staple food",
                    price=5.00,
                    stock=500,
                    category_id=categories[4].id
                ),
            ]
            
            for product in products:              
                await self.product_service.create_product(product)
            return products
        except Exception as e:
            print(f"❌ Error seeding products: {str(e)}")
            return []
    async def seed_all(self):
        try:
            # Seed users
            users = await self.seed_users()
            if not users:
                return False
            print("✅ Users seeded successfully!")

            # Seed categories
            categories = await self.seed_categories()
            print("✅ Database seeded successfully!")

            # Seed products
            products = await self.seed_products(categories)
            print("✅ Products seeded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error seeding database: {str(e)}")
            return False
