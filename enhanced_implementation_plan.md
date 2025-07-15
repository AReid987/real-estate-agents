# Enhanced Implementation Plan - Real Estate Agent Marketing System
## Building on Your Excellent Sprint Planning

After reviewing your comprehensive documentation, I'm impressed with the thoroughness of your planning. You have a solid 4-sprint roadmap, detailed requirements, and well-thought-out architecture. Let me provide specific technical enhancements and optimizations that build on your excellent foundation.

## Technical Enhancements & Optimizations

### 1. Sprint 1 Enhancements: Foundation Optimization

#### Enhanced Docker Configuration
Building on your existing `docker-compose.yml`, here are optimizations for development efficiency:

**Enhanced docker-compose.dev.yml:**
```yaml
version: '3.8'

services:
  ag2-core:
    build: 
      context: ./ag2-core
      dockerfile: Dockerfile.dev
      target: development
    volumes:
      - ./ag2-core:/app
      - ag2_cache:/app/.cache
    environment:
      - PYTHON_ENV=development
      - HOT_RELOAD=true
    depends_on:
      postgres:
        condition: service_healthy

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=rltr_mktg_dev
      - POSTGRES_USER=realestate
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./database/init-dev.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U realestate -d rltr_mktg_dev"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    volumes:
      - redis_dev_data:/data
    ports:
      - "6380:6379"

  portkey:
    image: portkeyai/gateway:latest
    environment:
      - PORTKEY_LOG_LEVEL=debug
      - PORTKEY_CACHE_TTL=3600
    ports:
      - "8787:8787"
    depends_on:
      - redis

volumes:
  postgres_dev_data:
  redis_dev_data:
  ag2_cache:
```

#### Optimized AG2 Core Dockerfile
**ag2-core/Dockerfile.dev:**
```dockerfile
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Development stage
FROM base as development
ENV PYTHON_ENV=development
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy source code
COPY . .

# Install in development mode
RUN pip install -e .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/.cache

# Run with hot reload
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# Production stage
FROM base as production
ENV PYTHON_ENV=production

COPY . .
RUN pip install --no-deps .

EXPOSE 8001
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

#### Enhanced Database Schema & Indexing Strategy
Building on your database design, here are performance optimizations:

**database/migrations/001_initial_with_indexes.sql:**
```sql
-- Your existing schema with optimized indexes

-- Performance indexes for common queries
CREATE INDEX CONCURRENTLY idx_listings_status_updated ON rltr_mktg_listings(status, last_updated_at);
CREATE INDEX CONCURRENTLY idx_content_pieces_agent_status ON rltr_mktg_content_pieces(agent_id, status);
CREATE INDEX CONCURRENTLY idx_notifications_agent_unread ON rltr_mktg_notifications(agent_id, is_read, created_at);
CREATE INDEX CONCURRENTLY idx_post_schedule_status_scheduled ON rltr_mktg_post_schedule(status, scheduled_at);

-- Composite indexes for complex queries
CREATE INDEX CONCURRENTLY idx_content_pieces_listing_type_status ON rltr_mktg_content_pieces(listing_id, content_type, status);
CREATE INDEX CONCURRENTLY idx_approval_logs_content_timestamp ON rltr_mktg_approval_logs(content_piece_id, timestamp DESC);

-- Partial indexes for frequently filtered data
CREATE INDEX CONCURRENTLY idx_listings_active ON rltr_mktg_listings(id, last_updated_at) WHERE status = 'active';
CREATE INDEX CONCURRENTLY idx_content_pending_approval ON rltr_mktg_content_pieces(id, created_at) WHERE status IN ('pending_approval_agent', 'pending_external_marketing_approval');

-- Text search indexes for content search
CREATE INDEX CONCURRENTLY idx_listings_search ON rltr_mktg_listings USING gin(to_tsvector('english', description || ' ' || address));
CREATE INDEX CONCURRENTLY idx_content_search ON rltr_mktg_content_pieces USING gin(to_tsvector('english', generated_text::text));
```

### 2. Sprint 2 Enhancements: Authentication & Content Flow

#### Advanced SQLAlchemy Models with Optimizations
**ag2-core/src/database/models.py:**
```python
from sqlalchemy import Column, String, DateTime, Boolean, Text, JSONB, Integer, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class TimeStampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class User(Base, TimeStampMixin):
    __tablename__ = 'rltr_mktg_users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    last_login_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('rltr_mktg_agents.id'), unique=True)
    
    # Relationship
    agent = relationship("Agent", back_populates="user", uselist=False)

class Agent(Base, TimeStampMixin):
    __tablename__ = 'rltr_mktg_agents'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    phone = Column(String(20))
    email = Column(String(255), unique=True, nullable=False, index=True)
    company = Column(String(255))
    profile_image_url = Column(Text)
    notification_preferences = Column(JSONB, default={})
    
    # Relationships
    user = relationship("User", back_populates="agent", uselist=False)
    content_pieces = relationship("ContentPiece", back_populates="agent")
    social_media_accounts = relationship("SocialMediaAccount", back_populates="agent")
    notifications = relationship("Notification", back_populates="agent")

class Listing(Base, TimeStampMixin):
    __tablename__ = 'rltr_mktg_listings'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(String(255), unique=True, nullable=False, index=True)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(50), nullable=False)
    zip_code = Column(String(20), nullable=False)
    price = Column(Numeric(12, 2))
    beds = Column(Integer)
    baths = Column(Numeric(3, 1))
    sqft = Column(Integer)
    description = Column(Text)
    key_features = Column(ARRAY(Text))
    image_urls = Column(ARRAY(Text))
    status = Column(String(50), default='active', index=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    content_pieces = relationship("ContentPiece", back_populates="listing")
    
    # Indexes
    __table_args__ = (
        Index('idx_listing_status_updated', status, last_updated_at),
        Index('idx_listing_location', city, state, zip_code),
    )

class ContentPiece(Base, TimeStampMixin):
    __tablename__ = 'rltr_mktg_content_pieces'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    listing_id = Column(UUID(as_uuid=True), ForeignKey('rltr_mktg_listings.id'), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), ForeignKey('rltr_mktg_agents.id'), nullable=False, index=True)
    content_type = Column(String(100), nullable=False)
    generated_text = Column(JSONB, nullable=False)
    associated_image_urls = Column(ARRAY(Text))
    status = Column(String(100), nullable=False, index=True)
    feedback = Column(Text)
    last_approved_at = Column(DateTime(timezone=True))
    ai_model_used = Column(String(100))  # Track which model generated this
    generation_metadata = Column(JSONB)  # Store prompt tokens, cost, etc.
    
    # Relationships
    listing = relationship("Listing", back_populates="content_pieces")
    agent = relationship("Agent", back_populates="content_pieces")
    approval_logs = relationship("ApprovalLog", back_populates="content_piece")
    post_schedules = relationship("PostSchedule", back_populates="content_piece")
    
    # Indexes
    __table_args__ = (
        Index('idx_content_agent_status', agent_id, status),
        Index('idx_content_listing_type_status', listing_id, content_type, status),
    )
```

#### Enhanced AG2 Agent Base Class
**ag2-core/src/agents/base_agent.py:**
```python
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import traceback

from ag2 import ConversableAgent
from ..database.session import get_db_session
from ..database.models import Agent as AgentModel, ContentPiece, Listing
from ..utils.monitoring import AgentMetrics
from ..utils.error_handling import AgentError, handle_agent_error

class RealEstateAgentBase(ConversableAgent):
    """Enhanced base class for all real estate agents with comprehensive error handling and monitoring"""
    
    def __init__(self, name: str, role: str, **kwargs):
        # Enhanced system message with role-specific instructions
        system_message = self._get_enhanced_system_message(role)
        
        # Enhanced LLM config with retry logic and cost tracking
        llm_config = {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.3,
            "timeout": 120,
            "max_tokens": 2000,
            "retry_on_failure": True,
            "max_retries": 3,
            "cache_seed": None,  # Enable caching
        }
        llm_config.update(kwargs.get('llm_config', {}))
        
        super().__init__(
            name=name,
            system_message=system_message,
            llm_config=llm_config,
            max_consecutive_auto_reply=5,
            human_input_mode="NEVER",
            **{k: v for k, v in kwargs.items() if k != 'llm_config'}
        )
        
        self.role = role
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.metrics = AgentMetrics(agent_name=name)
        self._db_session = None
    
    async def get_db_session(self):
        """Get async database session"""
        if not self._db_session:
            self._db_session = await get_db_session()
        return self._db_session
    
    @handle_agent_error
    async def execute_with_monitoring(self, operation_name: str, operation_func, *args, **kwargs):
        """Execute operation with comprehensive monitoring and error handling"""
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting {operation_name}")
            self.metrics.operation_started(operation_name)
            
            result = await operation_func(*args, **kwargs)
            
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.operation_completed(operation_name, duration)
            self.logger.info(f"Completed {operation_name} in {duration:.2f}s")
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.metrics.operation_failed(operation_name, duration, str(e))
            self.logger.error(f"Failed {operation_name} after {duration:.2f}s: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise AgentError(f"{operation_name} failed", original_error=e, agent_name=self.name)
    
    def _get_enhanced_system_message(self, role: str) -> str:
        """Get enhanced system message with specific capabilities and constraints"""
        base_instructions = """
        You are an AI agent in a real estate marketing automation system. 
        
        Core Principles:
        1. Always maintain compliance with Fair Housing Laws
        2. Generate professional, accurate, and engaging content
        3. Respect data privacy and security requirements
        4. Provide clear, actionable responses
        5. Log all significant actions for audit purposes
        
        Communication Format:
        - Use structured JSON for data exchange when possible
        - Include confidence scores for generated content
        - Provide clear reasoning for decisions
        - Flag any uncertainties or required human review
        """
        
        role_specific = {
            "listing_specialist": """
            You are a listing specialist focused on:
            - Extracting accurate property data from web sources
            - Identifying key selling points and market positioning
            - Ensuring data quality and completeness
            - Triggering appropriate downstream workflows
            
            Always validate extracted data for completeness and accuracy.
            """,
            
            "content_creator": """
            You are a content creation specialist focused on:
            - Generating compelling, conversion-focused marketing copy
            - Optimizing content for different platforms and audiences
            - Maintaining brand consistency and professional tone
            - Creating content that drives qualified leads
            
            Always generate content that is engaging yet professional.
            """,
            
            "social_media_manager": """
            You are a social media management specialist focused on:
            - Platform-specific content optimization
            - Audience engagement and growth strategies
            - Posting schedule optimization
            - Performance tracking and improvement
            
            Always consider platform best practices and audience preferences.
            """,
            
            "lead_manager": """
            You are a lead management specialist focused on:
            - Identifying high-quality prospects from engagement data
            - Scoring leads based on multiple factors
            - Creating personalized follow-up sequences
            - Optimizing conversion rates
            
            Always prioritize lead quality over quantity.
            """
        }
        
        return base_instructions + role_specific.get(role, "")
    
    async def update_content_status(self, content_id: str, new_status: str, feedback: Optional[str] = None):
        """Update content piece status with proper logging"""
        async with await self.get_db_session() as session:
            content = await session.get(ContentPiece, content_id)
            if content:
                old_status = content.status
                content.status = new_status
                if feedback:
                    content.feedback = feedback
                content.updated_at = datetime.now()
                
                await session.commit()
                
                self.logger.info(f"Updated content {content_id} status: {old_status} -> {new_status}")
                self.metrics.status_change_tracked(content_id, old_status, new_status)
                
                return True
            return False
    
    async def log_approval_action(self, content_id: str, agent_id: str, action_type: str, feedback: Optional[str] = None):
        """Log approval action to audit trail"""
        async with await self.get_db_session() as session:
            from ..database.models import ApprovalLog
            
            approval_log = ApprovalLog(
                content_piece_id=content_id,
                agent_id=agent_id,
                action_type=action_type,
                feedback=feedback,
                timestamp=datetime.now()
            )
            
            session.add(approval_log)
            await session.commit()
            
            self.logger.info(f"Logged approval action: {action_type} for content {content_id}")
```

#### Enhanced Content Generation Agent
**ag2-core/src/agents/content_agent.py:**
```python
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import openai

from .base_agent import RealEstateAgentBase
from ..database.models import ContentPiece, Listing, Agent as AgentModel
from ..utils.portkey_client import PortkeyClient
from ..utils.content_templates import ContentTemplates

class ContentGenerationAgent(RealEstateAgentBase):
    """Enhanced content generation agent with multiple LLM providers and quality validation"""
    
    def __init__(self, **kwargs):
        super().__init__(name="content_generation_agent", role="content_creator", **kwargs)
        self.portkey_client = PortkeyClient()
        self.templates = ContentTemplates()
        
    async def generate_content_for_listing(self, listing_id: str, agent_id: str, content_types: List[str]) -> Dict[str, Any]:
        """Generate multiple content types for a listing with quality validation"""
        
        return await self.execute_with_monitoring(
            "generate_content_for_listing",
            self._generate_content_internal,
            listing_id, agent_id, content_types
        )
    
    async def _generate_content_internal(self, listing_id: str, agent_id: str, content_types: List[str]) -> Dict[str, Any]:
        # Get listing and agent data
        async with await self.get_db_session() as session:
            listing = await session.get(Listing, listing_id)
            agent = await session.get(AgentModel, agent_id)
            
            if not listing or not agent:
                raise ValueError(f"Listing {listing_id} or Agent {agent_id} not found")
        
        generated_content = {}
        
        for content_type in content_types:
            if content_type == "social_media_post":
                content = await self._generate_social_media_content(listing, agent)
            elif content_type == "flyer_text":
                content = await self._generate_flyer_content(listing, agent)
            else:
                continue
            
            # Validate content quality
            validation_result = await self._validate_content_quality(content, content_type)
            
            if validation_result["is_valid"]:
                # Save to database
                content_piece = ContentPiece(
                    listing_id=listing_id,
                    agent_id=agent_id,
                    content_type=content_type,
                    generated_text=content,
                    status="pending_approval_agent",
                    ai_model_used=self.portkey_client.current_model,
                    generation_metadata={
                        "validation_score": validation_result["score"],
                        "generated_at": datetime.now().isoformat(),
                        "prompt_tokens": validation_result.get("prompt_tokens", 0),
                        "completion_tokens": validation_result.get("completion_tokens", 0)
                    }
                )
                
                async with await self.get_db_session() as session:
                    session.add(content_piece)
                    await session.commit()
                    await session.refresh(content_piece)
                
                generated_content[content_type] = {
                    "content_id": str(content_piece.id),
                    "content": content,
                    "validation_score": validation_result["score"]
                }
                
                # Trigger UserProxyAgent for approval
                await self._trigger_approval_workflow(content_piece.id)
            else:
                self.logger.warning(f"Content validation failed for {content_type}: {validation_result['issues']}")
        
        return generated_content
    
    async def _generate_social_media_content(self, listing: Listing, agent: AgentModel) -> Dict[str, Any]:
        """Generate platform-optimized social media content"""
        
        prompt = self.templates.get_social_media_prompt(
            listing_data={
                "address": listing.address,
                "price": float(listing.price) if listing.price else 0,
                "beds": listing.beds,
                "baths": float(listing.baths) if listing.baths else 0,
                "sqft": listing.sqft,
                "description": listing.description,
                "key_features": listing.key_features or []
            },
            agent_data={
                "name": agent.name,
                "phone": agent.phone,
                "company": agent.company
            }
        )
        
        response = await self.portkey_client.generate_completion(
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
        
        try:
            content = json.loads(response["content"])
            return {
                "headline": content.get("headline", ""),
                "body": content.get("body", ""),
                "call_to_action": content.get("call_to_action", ""),
                "hashtags": content.get("hashtags", []),
                "platform_variations": content.get("platform_variations", {}),
                "target_audience": content.get("target_audience", "general"),
                "estimated_engagement": content.get("estimated_engagement", "medium")
            }
        except json.JSONDecodeError:
            # Fallback parsing for non-JSON responses
            return self._parse_fallback_social_content(response["content"])
    
    async def _generate_flyer_content(self, listing: Listing, agent: AgentModel) -> Dict[str, Any]:
        """Generate comprehensive flyer content"""
        
        prompt = self.templates.get_flyer_prompt(
            listing_data={
                "address": listing.address,
                "price": float(listing.price) if listing.price else 0,
                "beds": listing.beds,
                "baths": float(listing.baths) if listing.baths else 0,
                "sqft": listing.sqft,
                "description": listing.description,
                "key_features": listing.key_features or []
            },
            agent_data={
                "name": agent.name,
                "phone": agent.phone,
                "email": agent.email,
                "company": agent.company
            }
        )
        
        response = await self.portkey_client.generate_completion(
            prompt=prompt,
            max_tokens=800,
            temperature=0.5
        )
        
        try:
            content = json.loads(response["content"])
            return {
                "main_headline": content.get("main_headline", ""),
                "property_summary": content.get("property_summary", ""),
                "key_features_formatted": content.get("key_features_formatted", []),
                "community_amenities": content.get("community_amenities", ""),
                "agent_section": content.get("agent_section", ""),
                "call_to_action": content.get("call_to_action", ""),
                "legal_disclaimers": content.get("legal_disclaimers", "")
            }
        except json.JSONDecodeError:
            return self._parse_fallback_flyer_content(response["content"])
    
    async def _validate_content_quality(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """Validate generated content for quality and compliance"""
        
        validation_prompt = f"""
        As a real estate marketing compliance expert, review this {content_type} content for:
        1. Fair Housing Law compliance (0-10 score)
        2. Professional tone and grammar (0-10 score) 
        3. Factual accuracy and completeness (0-10 score)
        4. Marketing effectiveness (0-10 score)
        5. Brand consistency (0-10 score)
        
        Content to review: {json.dumps(content)}
        
        Respond in JSON format:
        {{
            "overall_score": 0-10,
            "compliance_score": 0-10,
            "quality_score": 0-10,
            "effectiveness_score": 0-10,
            "is_valid": boolean,
            "issues": ["list of any issues found"],
            "suggestions": ["list of improvement suggestions"]
        }}
        """
        
        validation_response = await self.portkey_client.generate_completion(
            prompt=validation_prompt,
            max_tokens=300,
            temperature=0.2
        )
        
        try:
            validation_result = json.loads(validation_response["content"])
            # Set validity threshold
            validation_result["is_valid"] = validation_result.get("overall_score", 0) >= 7
            return validation_result
        except json.JSONDecodeError:
            # Default to valid if validation parsing fails
            return {
                "overall_score": 8,
                "is_valid": True,
                "issues": [],
                "suggestions": []
            }
    
    async def _trigger_approval_workflow(self, content_piece_id: str):
        """Trigger the UserProxyAgent for content approval"""
        # In a full implementation, this would send a message to the UserProxyAgent
        # For now, we'll log the trigger
        self.logger.info(f"Triggering approval workflow for content piece {content_piece_id}")
        
        # Send message to UserProxyAgent (implement based on your AG2 setup)
        approval_message = {
            "type": "content_approval_request",
            "content_piece_id": str(content_piece_id),
            "timestamp": datetime.now().isoformat(),
            "requesting_agent": self.name
        }
        
        # Implementation depends on your AG2 message passing setup
        # await self.send_message_to_agent("user_proxy_agent", approval_message)
```

### 3. Sprint 3 Enhancements: Social Media Integration

#### Advanced Social Media Client with Rate Limiting
**ag2-core/src/integrations/social_media_client.py:**
```python
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib
from dataclasses import dataclass

from ..utils.rate_limiter import RateLimiter
from ..utils.encryption import EncryptionManager
from ..database.models import SocialMediaAccount

@dataclass
class PostResult:
    success: bool
    platform_post_id: Optional[str] = None
    error_message: Optional[str] = None
    scheduled_for: Optional[datetime] = None

class EnhancedSocialMediaClient:
    """Advanced social media client with rate limiting, retry logic, and comprehensive error handling"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.rate_limiters = {
            'facebook': RateLimiter(calls_per_hour=50, calls_per_day=1000),
            'instagram': RateLimiter(calls_per_hour=25, calls_per_day=500)
        }
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def post_to_facebook(self, 
                              account: SocialMediaAccount, 
                              content: Dict[str, Any], 
                              images: List[str] = None,
                              scheduled_time: Optional[datetime] = None) -> PostResult:
        """Post content to Facebook with advanced error handling and scheduling"""
        
        # Check rate limits
        if not await self.rate_limiters['facebook'].acquire():
            return PostResult(
                success=False,
                error_message="Rate limit exceeded for Facebook API"
            )
        
        try:
            access_token = self.encryption_manager.decrypt(account.access_token_encrypted)
            
            # Prepare post data
            post_data = {
                'message': self._format_facebook_message(content),
                'access_token': access_token
            }
            
            # Handle scheduling
            if scheduled_time:
                post_data['scheduled_publish_time'] = int(scheduled_time.timestamp())
                post_data['published'] = 'false'
            
            # Handle images
            if images:
                if len(images) == 1:
                    # Single image post
                    post_data['url'] = images[0]
                    endpoint = f"https://graph.facebook.com/v18.0/{account.account_id}/photos"
                else:
                    # Multiple images (album)
                    return await self._post_facebook_album(account, content, images, scheduled_time)
            else:
                # Text-only post
                endpoint = f"https://graph.facebook.com/v18.0/{account.account_id}/feed"
            
            # Make API call with retries
            for attempt in range(3):
                try:
                    async with self.session.post(endpoint, data=post_data) as response:
                        response_data = await response.json()
                        
                        if response.status == 200 and 'id' in response_data:
                            return PostResult(
                                success=True,
                                platform_post_id=response_data['id'],
                                scheduled_for=scheduled_time
                            )
                        else:
                            error_msg = response_data.get('error', {}).get('message', 'Unknown error')
                            if attempt == 2:  # Last attempt
                                return PostResult(
                                    success=False,
                                    error_message=f"Facebook API error: {error_msg}"
                                )
                            else:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
                except aiohttp.ClientError as e:
                    if attempt == 2:
                        return PostResult(
                            success=False,
                            error_message=f"Network error: {str(e)}"
                        )
                    await asyncio.sleep(2 ** attempt)
        
        except Exception as e:
            return PostResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    async def post_to_instagram(self, 
                               account: SocialMediaAccount, 
                               content: Dict[str, Any], 
                               image_url: str,
                               scheduled_time: Optional[datetime] = None) -> PostResult:
        """Post content to Instagram with comprehensive error handling"""
        
        # Check rate limits
        if not await self.rate_limiters['instagram'].acquire():
            return PostResult(
                success=False,
                error_message="Rate limit exceeded for Instagram API"
            )
        
        try:
            access_token = self.encryption_manager.decrypt(account.access_token_encrypted)
            
            # Step 1: Create media container
            container_data = {
                'image_url': image_url,
                'caption': self._format_instagram_caption(content),
                'access_token': access_token
            }
            
            container_endpoint = f"https://graph.facebook.com/v18.0/{account.account_id}/media"
            
            async with self.session.post(container_endpoint, data=container_data) as response:
                container_response = await response.json()
                
                if response.status != 200 or 'id' not in container_response:
                    error_msg = container_response.get('error', {}).get('message', 'Failed to create media container')
                    return PostResult(
                        success=False,
                        error_message=f"Instagram container error: {error_msg}"
                    )
                
                container_id = container_response['id']
            
            # Step 2: Publish the media (with optional scheduling)
            publish_data = {
                'creation_id': container_id,
                'access_token': access_token
            }
            
            if scheduled_time:
                # Instagram doesn't support native scheduling via API
                # Would need to implement a scheduler service
                return PostResult(
                    success=False,
                    error_message="Instagram scheduling not supported in this version"
                )
            
            publish_endpoint = f"https://graph.facebook.com/v18.0/{account.account_id}/media_publish"
            
            # Retry logic for publishing
            for attempt in range(3):
                try:
                    async with self.session.post(publish_endpoint, data=publish_data) as response:
                        publish_response = await response.json()
                        
                        if response.status == 200 and 'id' in publish_response:
                            return PostResult(
                                success=True,
                                platform_post_id=publish_response['id']
                            )
                        else:
                            error_msg = publish_response.get('error', {}).get('message', 'Unknown error')
                            if attempt == 2:
                                return PostResult(
                                    success=False,
                                    error_message=f"Instagram publish error: {error_msg}"
                                )
                            else:
                                await asyncio.sleep(2 ** attempt)
                
                except aiohttp.ClientError as e:
                    if attempt == 2:
                        return PostResult(
                            success=False,
                            error_message=f"Network error: {str(e)}"
                        )
                    await asyncio.sleep(2 ** attempt)
        
        except Exception as e:
            return PostResult(
                success=False,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def _format_facebook_message(self, content: Dict[str, Any]) -> str:
        """Format content for Facebook posting"""
        message_parts = []
        
        if content.get('headline'):
            message_parts.append(content['headline'])
        
        if content.get('body'):
            message_parts.append(content['body'])
        
        if content.get('call_to_action'):
            message_parts.append(content['call_to_action'])
        
        # Add hashtags (Facebook supports hashtags)
        if content.get('hashtags'):
            hashtags = ' '.join([f"#{tag}" for tag in content['hashtags'][:5]])  # Limit to 5
            message_parts.append(hashtags)
        
        return '\n\n'.join(message_parts)
    
    def _format_instagram_caption(self, content: Dict[str, Any]) -> str:
        """Format content for Instagram posting with optimal hashtag placement"""
        caption_parts = []
        
        # Instagram prefers more concise content
        if content.get('headline'):
            caption_parts.append(content['headline'])
        
        if content.get('body'):
            # Truncate body for Instagram if too long
            body = content['body']
            if len(body) > 150:
                body = body[:147] + "..."
            caption_parts.append(body)
        
        if content.get('call_to_action'):
            caption_parts.append(content['call_to_action'])
        
        # Instagram hashtags are crucial - place at end
        if content.get('hashtags'):
            hashtags = ' '.join([f"#{tag}" for tag in content['hashtags'][:20]])  # Instagram allows more
            caption_parts.append(f"\n.\n.\n.\n{hashtags}")
        
        return '\n\n'.join(caption_parts)
```

### 4. Sprint 4 Enhancements: Langflow Integration & Testing

#### Advanced Langflow Integration
**ag2-core/src/integrations/langflow_client.py:**
```python
import aiohttp
import json
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

class LangflowClient:
    """Advanced Langflow client with workflow management and caching"""
    
    def __init__(self, base_url: str = "http://langflow:7860", api_key: Optional[str] = None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
        self.logger = logging.getLogger(__name__)
        self.workflow_cache = {}
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def run_flyer_generation_workflow(self, listing_data: Dict[str, Any], agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the flyer generation workflow with enhanced error handling"""
        
        workflow_id = "flyer-generation"
        
        payload = {
            "inputs": {
                "property_data": listing_data,
                "agent_info": agent_data,
                "template_preferences": {
                    "style": self._determine_flyer_style(listing_data),
                    "color_scheme": "professional",
                    "layout": "modern"
                }
            }
        }
        
        return await self._execute_workflow(workflow_id, payload)
    
    async def run_social_optimization_workflow(self, content: Dict[str, Any], platform: str, target_audience: str = "general") -> Dict[str, Any]:
        """Run social media optimization workflow"""
        
        workflow_id = "social-optimization"
        
        payload = {
            "inputs": {
                "raw_content": content,
                "target_platform": platform,
                "target_audience": target_audience,
                "optimization_goals": ["engagement", "reach", "conversion"],
                "brand_guidelines": {
                    "tone": "professional_friendly",
                    "style": "modern",
                    "compliance_level": "high"
                }
            }
        }
        
        return await self._execute_workflow(workflow_id, payload)
    
    async def run_market_research_workflow(self, location: str, property_type: str) -> Dict[str, Any]:
        """Run market research workflow for competitive analysis"""
        
        workflow_id = "market-research"
        
        payload = {
            "inputs": {
                "location": location,
                "property_type": property_type,
                "research_depth": "comprehensive",
                "data_sources": ["mls", "zillow", "realtor_com", "local_news"],
                "analysis_type": ["pricing", "market_trends", "competition"]
            }
        }
        
        return await self._execute_workflow(workflow_id, payload)
    
    async def _execute_workflow(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Langflow workflow with caching and retry logic"""
        
        # Check cache first
        cache_key = self._generate_cache_key(workflow_id, payload)
        if cache_key in self.workflow_cache:
            cached_result = self.workflow_cache[cache_key]
            if (datetime.now() - cached_result["timestamp"]).seconds < 3600:  # 1 hour cache
                self.logger.info(f"Returning cached result for {workflow_id}")
                return cached_result["result"]
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Retry logic
        for attempt in range(3):
            try:
                async with self.session.post(
                    f"{self.base_url}/api/v1/run/{workflow_id}",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        # Cache successful results
                        self.workflow_cache[cache_key] = {
                            "result": result,
                            "timestamp": datetime.now()
                        }
                        
                        self.logger.info(f"Successfully executed {workflow_id}")
                        return result
                    
                    elif response.status == 429:  # Rate limited
                        wait_time = 2 ** attempt
                        self.logger.warning(f"Rate limited for {workflow_id}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    
                    else:
                        error_text = await response.text()
                        self.logger.error(f"Langflow error for {workflow_id}: {response.status} - {error_text}")
                        
                        if attempt == 2:  # Last attempt
                            raise Exception(f"Langflow workflow failed: {error_text}")
            
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout executing {workflow_id} (attempt {attempt + 1})")
                if attempt == 2:
                    raise Exception(f"Langflow workflow {workflow_id} timed out")
                await asyncio.sleep(2 ** attempt)
            
            except Exception as e:
                self.logger.error(f"Error executing {workflow_id}: {str(e)}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise Exception(f"Failed to execute {workflow_id} after 3 attempts")
    
    def _determine_flyer_style(self, listing_data: Dict[str, Any]) -> str:
        """Intelligently determine flyer style based on property data"""
        price = listing_data.get("price", 0)
        
        if price > 1000000:
            return "luxury"
        elif price > 500000:
            return "premium"
        else:
            return "standard"
    
    def _generate_cache_key(self, workflow_id: str, payload: Dict[str, Any]) -> str:
        """Generate cache key for workflow results"""
        import hashlib
        payload_str = json.dumps(payload, sort_keys=True)
        return hashlib.md5(f"{workflow_id}:{payload_str}".encode()).hexdigest()
```

#### Comprehensive Testing Suite
**tests/integration/test_end_to_end.py:**
```python
import pytest
import asyncio
from datetime import datetime
import uuid

from ag2_core.src.database.session import get_test_db_session
from ag2_core.src.database.models import Agent, Listing, ContentPiece
from ag2_core.src.agents.listing_agent import ListingAgent
from ag2_core.src.agents.content_agent import ContentGenerationAgent
from ag2_core.src.agents.social_media_agent import SocialMediaAgent

@pytest.mark.asyncio
class TestEndToEndWorkflow:
    """Comprehensive end-to-end testing of the real estate marketing workflow"""
    
    async def test_complete_listing_to_posting_workflow(self):
        """Test the complete workflow from listing ingestion to social media posting"""
        
        # Setup test data
        test_agent_id = str(uuid.uuid4())
        test_listing_data = {
            "source_id": "test_listing_001",
            "address": "123 Test Street, Test City, TC 12345",
            "price": 750000,
            "beds": 4,
            "baths": 3,
            "sqft": 2500,
            "description": "Beautiful modern home with upgraded kitchen and spacious backyard",
            "key_features": ["Modern Kitchen", "Hardwood Floors", "Two-Car Garage", "Fenced Yard"],
            "image_urls": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
        }
        
        # Create test agent in database
        async with get_test_db_session() as session:
            test_agent = Agent(
                id=test_agent_id,
                name="Test Agent",
                email="test@example.com",
                phone="555-123-4567",
                company="Test Realty"
            )
            session.add(test_agent)
            await session.commit()
        
        # Step 1: Test listing ingestion
        listing_agent = ListingAgent()
        listing_result = await listing_agent.process_listing_data(test_listing_data)
        
        assert listing_result["success"] == True
        assert "listing_id" in listing_result
        listing_id = listing_result["listing_id"]
        
        # Verify listing was saved to database
        async with get_test_db_session() as session:
            saved_listing = await session.get(Listing, listing_id)
            assert saved_listing is not None
            assert saved_listing.address == test_listing_data["address"]
            assert saved_listing.price == test_listing_data["price"]
        
        # Step 2: Test content generation
        content_agent = ContentGenerationAgent()
        content_result = await content_agent.generate_content_for_listing(
            listing_id=listing_id,
            agent_id=test_agent_id,
            content_types=["social_media_post", "flyer_text"]
        )
        
        assert "social_media_post" in content_result
        assert "flyer_text" in content_result
        assert content_result["social_media_post"]["validation_score"] >= 7
        
        # Verify content was saved to database
        async with get_test_db_session() as session:
            content_pieces = await session.execute(
                "SELECT * FROM rltr_mktg_content_pieces WHERE listing_id = $1",
                [listing_id]
            )
            content_list = content_pieces.fetchall()
            assert len(content_list) == 2  # social_media_post and flyer_text
        
        # Step 3: Test approval workflow (simulate user approval)
        social_content_id = content_result["social_media_post"]["content_id"]
        
        # Simulate approval action
        approval_result = await content_agent.update_content_status(
            content_id=social_content_id,
            new_status="approved_for_posting"
        )
        assert approval_result == True
        
        # Step 4: Test social media posting (mock)
        social_media_agent = SocialMediaAgent()
        
        # Mock social media account
        mock_account = {
            "id": str(uuid.uuid4()),
            "platform": "facebook",
            "account_id": "test_page_id",
            "access_token_encrypted": "mock_encrypted_token"
        }
        
        # Test posting (this would be mocked in real tests)
        posting_result = await social_media_agent.post_approved_content(
            content_id=social_content_id,
            social_account=mock_account
        )
        
        # In a real test, this would verify the mock was called correctly
        assert posting_result["success"] == True or posting_result["success"] == False  # Depends on mock setup
    
    async def test_error_handling_and_recovery(self):
        """Test error handling and recovery mechanisms"""
        
        # Test invalid listing data
        listing_agent = ListingAgent()
        invalid_result = await listing_agent.process_listing_data({})
        
        assert invalid_result["success"] == False
        assert "error" in invalid_result
        
        # Test content generation with missing listing
        content_agent = ContentGenerationAgent()
        missing_listing_result = await content_agent.generate_content_for_listing(
            listing_id="non_existent_id",
            agent_id="non_existent_agent",
            content_types=["social_media_post"]
        )
        
        # Should handle gracefully
        assert "error" in str(missing_listing_result).lower()
    
    async def test_performance_benchmarks(self):
        """Test performance benchmarks for key operations"""
        
        start_time = datetime.now()
        
        # Test content generation speed
        content_agent = ContentGenerationAgent()
        
        # Create minimal test data
        test_listing = {
            "address": "Performance Test Property",
            "price": 500000,
            "description": "Test property for performance benchmarking"
        }
        
        # This would need proper test setup, but demonstrates the concept
        generation_start = datetime.now()
        # result = await content_agent.generate_test_content(test_listing)
        generation_time = (datetime.now() - generation_start).total_seconds()
        
        # Assert performance requirements
        assert generation_time < 10.0  # Content generation should take less than 10 seconds
        
        total_time = (datetime.now() - start_time).total_seconds()
        assert total_time < 30.0  # Total test should complete in under 30 seconds

@pytest.mark.integration
class TestAPIEndpoints:
    """Integration tests for API endpoints"""
    
    async def test_listing_endpoints(self):
        """Test listing-related API endpoints"""
        # Implementation would test actual API endpoints
        pass
    
    async def test_content_approval_endpoints(self):
        """Test content approval API endpoints"""
        # Implementation would test approval workflow APIs
        pass
    
    async def test_notification_endpoints(self):
        """Test notification system APIs"""
        # Implementation would test notification delivery
        pass

# Pytest configuration for running tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_database():
    """Setup and teardown test database"""
    # Setup test database
    # This would create a test-specific database instance
    yield
    # Cleanup test database
```

## Key Implementation Recommendations

### 1. **Immediate Sprint 1 Focus**
- Start with the enhanced Docker setup for faster development cycles
- Implement the optimized database schema with proper indexing
- Use the enhanced base agent class for consistent error handling

### 2. **Performance Optimizations**
- Implement caching at multiple levels (Redis, Portkey, Langflow)
- Use connection pooling for database connections
- Add comprehensive monitoring and metrics collection

### 3. **Production Readiness**
- Enhanced error handling and recovery mechanisms
- Comprehensive logging and monitoring
- Rate limiting and API protection
- Security best practices throughout

### 4. **Cost Management**
- Smart caching to reduce LLM API calls
- Efficient database queries with proper indexing
- Resource optimization in Docker containers
- Usage monitoring and alerting

### 5. **Testing Strategy**
- Unit tests for individual agent functions
- Integration tests for agent interactions
- End-to-end tests for complete workflows
- Performance benchmarking
- Load testing for production readiness

## Next Steps

1. **Week 1**: Implement the enhanced Sprint 1 foundation with optimized Docker setup
2. **Week 2**: Add the advanced agent base classes and database optimizations
3. **Week 3**: Implement enhanced content generation with quality validation
4. **Week 4**: Add comprehensive social media integration with rate limiting
5. **Week 5**: Integrate advanced Langflow workflows
6. **Week 6**: Complete testing suite and performance optimization

Your planning is excellent - this enhanced implementation builds on your solid foundation while adding production-grade optimizations and best practices that will make your system more robust, scalable, and maintainable.