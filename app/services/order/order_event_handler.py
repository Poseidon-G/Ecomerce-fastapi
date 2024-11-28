from typing import Dict, Any
from app.models import Order
from app.services.order.order_service import OrderService
from app.database.connection import get_db
from app.utils.logger import logger
from enum import Enum
import asyncio

class OrderStatus(Enum):
    CREATED = "created"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

async def process_order(order_data: Dict[str, Any]):
    """
    Process order messages from Kafka
    Args:
        order_data: Dictionary containing order information
    """
    try:
        # Validate required fields
        required_fields = ["order_id", "status", "customer_id"]
        if not all(field in order_data for field in required_fields):
            logger.error(f"Missing required fields in order data: {order_data}")
            return

        order_id = order_data["order_id"]
        status = order_data["status"]
        
        # Get database session
        async with get_db() as db:
            order_service = OrderService(db)
            
            # Get existing order
            order = await order_service.get_order(order_id)
            if not order:
                logger.error(f"Order not found: {order_id}")
                return

            # Update order status
            try:
                new_status = OrderStatus(status.lower())
                await order_service.update_order_status(order_id, new_status)
                logger.info(f"Updated order {order_id} status to {new_status.value}")

                # Handle status-specific actions
                if new_status == OrderStatus.PAID:
                    await _handle_paid_order(order_data, order_service)
                elif new_status == OrderStatus.SHIPPED:
                    await _handle_shipped_order(order_data, order_service)
                elif new_status == OrderStatus.CANCELLED:
                    await _handle_cancelled_order(order_data, order_service)

            except ValueError as e:
                logger.error(f"Invalid order status: {status}")
                return

    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        # Could implement retry logic here
        raise

async def _handle_paid_order(order_data: Dict[str, Any], order_service: OrderService):
    """Handle paid order specific logic"""
    # Update inventory
    await order_service.update_inventory(order_data["order_id"])
    # Send confirmation email
    await order_service.send_payment_confirmation(order_data["customer_id"])

async def _handle_shipped_order(order_data: Dict[str, Any], order_service: OrderService):
    """Handle shipped order specific logic"""
    # Send tracking information
    await order_service.send_shipping_notification(
        order_data["order_id"],
        order_data.get("tracking_number")
    )

async def _handle_cancelled_order(order_data: Dict[str, Any], order_service: OrderService):
    """Handle cancelled order specific logic"""
    # Restore inventory
    await order_service.restore_inventory(order_data["order_id"])
    # Process refund if needed
    if order_data.get("refund_required"):
        await order_service.process_refund(order_data["order_id"])