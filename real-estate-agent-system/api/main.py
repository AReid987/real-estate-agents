"""
API Gateway for Real Estate Agent Marketing System
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import httpx
import structlog
from database.connection import init_database
from auth import get_current_user, create_access_token
from models import *
from config import settings

logger = structlog.get_logger()

# Initialize HTTP client for AG2 communication
ag2_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global ag2_client
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized")
        
        # Initialize HTTP client for AG2 communication
        ag2_client = httpx.AsyncClient(
            base_url=settings.ag2_core_url,
            timeout=30.0
        )
        logger.info("AG2 client initialized")
        
        yield
        
    except Exception as e:
        logger.error("Failed to initialize application", error=str(e))
        raise
    finally:
        # Cleanup
        if ag2_client:
            await ag2_client.aclose()
        logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Real Estate Agent Marketing System - API Gateway",
    description="API Gateway for managing real estate content marketing and social media",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }

# Authentication endpoints
@app.post("/auth/login", response_model=TokenResponse)
async def login(user_credentials: UserLogin):
    """User login endpoint"""
    try:
        # TODO: Implement actual authentication
        # For now, return a mock token
        access_token = create_access_token(data={"sub": user_credentials.email})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer"
        )
        
    except Exception as e:
        logger.error("Login failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@app.get("/auth/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    return UserProfile(
        id="mock-user-id",
        email=current_user.get("sub", "user@example.com"),
        name="Mock User",
        agent_id="mock-agent-id"
    )

# Listing endpoints
@app.get("/listings", response_model=List[ListingResponse])
async def get_listings(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get property listings"""
    try:
        # For now, return mock data
        # TODO: Implement actual database query
        listings = [
            ListingResponse(
                id="1",
                source_id="holiday_1",
                address={
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state_zip": "CA 90210",
                    "full_address": "123 Main St, Anytown, CA 90210"
                },
                price=500000,
                beds=3,
                baths=2,
                sqft=1500,
                description="Beautiful family home",
                key_features=["Swimming Pool", "Granite Counters"],
                image_urls=["https://example.com/image1.jpg"],
                status="active"
            )
        ]
        
        return listings
        
    except Exception as e:
        logger.error("Failed to get listings", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/listings/{listing_id}/generate-content")
async def generate_content_for_listing(
    listing_id: str,
    content_request: ContentGenerationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate marketing content for a listing"""
    try:
        # Forward request to AG2 core
        response = await ag2_client.post(
            "/agents/generate-content",
            json={
                "listing_id": listing_id,
                "content_type": content_request.content_type,
                "agent_id": current_user.get("agent_id", "mock-agent-id")
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to generate content"
            )
            
    except httpx.RequestError as e:
        logger.error("Failed to communicate with AG2 core", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")
    except Exception as e:
        logger.error("Failed to generate content", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Content approval endpoints
@app.get("/content/pending")
async def get_pending_content(current_user: dict = Depends(get_current_user)):
    """Get content pending approval"""
    try:
        # Forward request to AG2 core
        response = await ag2_client.get(
            f"/agents/pending-approvals?agent_id={current_user.get('agent_id', 'mock-agent-id')}"
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to get pending content"
            )
            
    except httpx.RequestError as e:
        logger.error("Failed to communicate with AG2 core", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/content/{content_id}/approve")
async def approve_content(
    content_id: str,
    approval: ContentApproval,
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject content"""
    try:
        # Forward request to AG2 core
        response = await ag2_client.post(
            "/agents/approve-content",
            json={
                "content_id": content_id,
                "agent_id": current_user.get("agent_id", "mock-agent-id"),
                "approved": approval.approved,
                "feedback": approval.feedback
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to process approval"
            )
            
    except httpx.RequestError as e:
        logger.error("Failed to communicate with AG2 core", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

# Social media account endpoints
@app.get("/social-media/accounts")
async def get_social_media_accounts(current_user: dict = Depends(get_current_user)):
    """Get user's social media accounts"""
    try:
        # TODO: Implement actual database query
        accounts = [
            SocialMediaAccountResponse(
                id="1",
                platform="facebook",
                platform_account_id="facebook_123",
                active=True
            ),
            SocialMediaAccountResponse(
                id="2",
                platform="instagram",
                platform_account_id="instagram_456",
                active=True
            )
        ]
        
        return accounts
        
    except Exception as e:
        logger.error("Failed to get social media accounts", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/social-media/accounts")
async def add_social_media_account(
    account: SocialMediaAccountCreate,
    current_user: dict = Depends(get_current_user)
):
    """Add a new social media account"""
    try:
        # TODO: Implement actual account creation
        # This would involve OAuth flow for the specific platform
        
        return {
            "status": "success",
            "message": "Social media account added successfully",
            "account_id": "new-account-id"
        }
        
    except Exception as e:
        logger.error("Failed to add social media account", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Notification endpoints
@app.get("/notifications")
async def get_notifications(
    limit: int = 20,
    unread_only: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        # TODO: Implement actual database query
        notifications = [
            NotificationResponse(
                id="1",
                notification_type="content_approval_request",
                message_text="New content ready for approval",
                is_read=False,
                created_at="2024-01-01T12:00:00Z"
            )
        ]
        
        return notifications
        
    except Exception as e:
        logger.error("Failed to get notifications", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        # TODO: Implement actual database update
        
        return {
            "status": "success",
            "message": "Notification marked as read"
        }
        
    except Exception as e:
        logger.error("Failed to mark notification as read", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

# Post scheduling endpoints
@app.post("/posts/schedule")
async def schedule_post(
    post_schedule: PostScheduleRequest,
    current_user: dict = Depends(get_current_user)
):
    """Schedule a post for social media"""
    try:
        # Forward request to AG2 core
        response = await ag2_client.post(
            "/agents/schedule-post",
            json={
                "content_piece_id": post_schedule.content_piece_id,
                "social_media_account_id": post_schedule.social_media_account_id,
                "scheduled_time": post_schedule.scheduled_time
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail="Failed to schedule post"
            )
            
    except httpx.RequestError as e:
        logger.error("Failed to communicate with AG2 core", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.get("/posts/scheduled")
async def get_scheduled_posts(current_user: dict = Depends(get_current_user)):
    """Get scheduled posts"""
    try:
        # TODO: Implement actual database query
        posts = [
            ScheduledPostResponse(
                id="1",
                content_piece_id="content-1",
                social_media_account_id="account-1",
                platform="facebook",
                scheduled_at="2024-01-01T15:00:00Z",
                status="pending"
            )
        ]
        
        return posts
        
    except Exception as e:
        logger.error("Failed to get scheduled posts", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)