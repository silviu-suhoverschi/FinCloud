"""
Event schemas for event queue
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Event types"""

    BUDGET_THRESHOLD_EXCEEDED = "budget_threshold_exceeded"
    BUDGET_THRESHOLD_WARNING = "budget_threshold_warning"
    TRANSACTION_CREATED = "transaction_created"
    TRANSACTION_LARGE = "transaction_large"
    PORTFOLIO_VALUE_CHANGED = "portfolio_value_changed"
    PRICE_TARGET_HIT = "price_target_hit"
    PRICE_ALERT = "price_alert"
    SYSTEM_UPDATE = "system_update"
    SYSTEM_MAINTENANCE = "system_maintenance"
    USER_ACTION_REQUIRED = "user_action_required"


class NotificationEvent(BaseModel):
    """Notification event for queue processing"""

    event_id: str = Field(default_factory=lambda: f"evt_{datetime.utcnow().timestamp()}")
    event_type: EventType
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: dict[str, Any]
    priority: int = Field(default=1, ge=1, le=5)
    retry_count: int = 0
    max_retries: int = 3

    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "evt_1234567890",
                "event_type": "budget_threshold_exceeded",
                "user_id": "user123",
                "timestamp": "2025-11-14T10:00:00",
                "data": {
                    "budget_name": "Groceries",
                    "spent": 520.00,
                    "limit": 500.00,
                    "percentage": 104.0,
                },
                "priority": 2,
            }
        }
