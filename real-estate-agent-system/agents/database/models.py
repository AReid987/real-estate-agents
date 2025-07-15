"""
Database models for the Real Estate Agent Marketing System
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# Mock models for now - these would be SQLAlchemy models in production

class Agent:
    def __init__(self, id: str, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email

class Listing:
    def __init__(self, id: str, source_id: str, address: Dict[str, Any], price: float = None):
        self.id = id
        self.source_id = source_id
        self.address = address
        self.price = price
        self.status = "active"

class ContentPiece:
    def __init__(self, id: str, listing_id: str, agent_id: str, content_type: str):
        self.id = id
        self.listing_id = listing_id
        self.agent_id = agent_id
        self.content_type = content_type
        self.status = "draft"
        self.generated_text = {}

class SocialMediaAccount:
    def __init__(self, id: str, agent_id: str, platform: str):
        self.id = id
        self.agent_id = agent_id
        self.platform = platform
        self.active = True

class PostSchedule:
    def __init__(self, id: str, content_piece_id: str, social_media_account_id: str):
        self.id = id
        self.content_piece_id = content_piece_id
        self.social_media_account_id = social_media_account_id
        self.status = "pending"

class ApprovalLog:
    def __init__(self, id: str, content_piece_id: str, agent_id: str, action_type: str):
        self.id = id
        self.content_piece_id = content_piece_id
        self.agent_id = agent_id
        self.action_type = action_type

class Notification:
    def __init__(self, id: str, agent_id: str, notification_type: str, message_text: str):
        self.id = id
        self.agent_id = agent_id
        self.notification_type = notification_type
        self.message_text = message_text
        self.is_read = False