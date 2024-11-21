from sqlalchemy import Column, Float, ForeignKey, String, Boolean, DateTime, Integer, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base
from app.core.security import get_password_hash, verify_password
from sqlalchemy.ext.hybrid import hybrid_property
from app.utils.text import slugify  

class UserRole(enum.Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    STAFF = "staff"

from sqlalchemy.dialects.postgresql import ENUM
role_type = ENUM('admin', 'customer', 'staff', name='userrole', create_type=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile fields
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20), nullable=True) #Add migration to update this field
    role = Column(role_type, default=UserRole.CUSTOMER)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    
    # Password handling
    def set_password(self, password: str):
        self.password_hash = get_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password_hash)
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<User {self.email}>"
    

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    sku = Column(String(50), unique=True, index=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
        
    def __repr__(self):
        return f"<Product {self.name}>"
    
class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    slug = Column(String(100), nullable=False, unique=True) # Add migration to update this field
    
    # Use string literals for relationships
    products = relationship("Product", back_populates="category")
    parent = relationship(
        "Category",
        remote_side=[id],
        backref="children"
    )
    
    @hybrid_property
    def slug(self):
        return slugify(self.name)
    
    def __repr__(self):
        return f"<Category {self.name}>"
    
class Order(Base): #Add migration to update this field
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)
    is_shipped = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    
    def __repr__(self):
        return f"<Order {self.id}>"
    
class OrderItem(Base): #Add migration to update this field
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")
    
    def __repr__(self):
        return f"<OrderItem {self.id}>"

class Review(Base): #Add migration to update this field
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    user = relationship("User")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<Review {self.id}>"
