"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Authentication models
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    agent_id: Optional[str] = None

# Listing models
class AddressData(BaseModel):
    street: str
    city: str
    state_zip: str
    full_address: str

class ListingResponse(BaseModel):
    id: str
    source_id: str
    address: AddressData
    price: Optional[float] = None
    beds: Optional[int] = None
    baths: Optional[int] = None
    sqft: Optional[int] = None
    description: Optional[str] = None
    key_features: List[str] = []
    image_urls: List[str] = []
    status: str

# Content models
class ContentGenerationRequest(BaseModel):
    content_type: str  # social_media_post, flyer_text, property_description, email_campaign

class ContentApproval(BaseModel):
    approved: bool
    feedback: Optional[str] = None

class ContentPieceResponse(BaseModel):
    id: str
    listing_id: str
    content_type: str
    generated_text: Dict[str, Any]
    status: str
    created_at: str
    feedback: Optional[str] = None

# Social media models
class SocialMediaAccountCreate(BaseModel):
    platform: str
    access_token: str
    platform_account_id: str

class SocialMediaAccountResponse(BaseModel):
    id: str
    platform: str
    platform_account_id: str
    active: bool

# Notification models
class NotificationResponse(BaseModel):
    id: str
    notification_type: str
    message_text: str
    is_read: bool
    created_at: str
    related_entity_id: Optional[str] = None

# Post scheduling models
class PostScheduleRequest(BaseModel):
    content_piece_id: str
    social_media_account_id: str
    scheduled_time: Optional[str] = None

class ScheduledPostResponse(BaseModel):
    id: str
    content_piece_id: str
    social_media_account_id: str
    platform: str
    scheduled_at: str
    status: str
    posted_at: Optional[str] = None
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None