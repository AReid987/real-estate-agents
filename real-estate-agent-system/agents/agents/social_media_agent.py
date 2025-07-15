"""
Social Media Agent - Responsible for managing social media posting
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select
from database.models import PostSchedule, ContentPiece
from agents.agents.base_agent import BaseRealEstateAgent
import structlog

logger = structlog.get_logger()

class SocialMediaAgent(BaseRealEstateAgent):
    """Agent responsible for posting content to social media platforms"""
    
    def __init__(self):
        system_message = """
        You are a Social Media Agent specialized in managing real estate social media presence.
        Your responsibilities include scheduling posts, managing posting schedules, and handling errors.
        """
        
        super().__init__(
            name="SocialMediaAgent",
            description="Manages social media posting and engagement",
            system_message=system_message
        )
        
    async def schedule_post(
        self,
        content_piece_id: str,
        social_media_account_id: str,
        scheduled_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Schedule a post for a specific social media account"""
        task_id = f"schedule_post_{content_piece_id}"
        
        return await self.execute_task(
            task_id,
            self._schedule_post_task,
            content_piece_id,
            social_media_account_id,
            scheduled_time
        )
        
    async def _schedule_post_task(
        self,
        content_piece_id: str,
        social_media_account_id: str,
        scheduled_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Internal task for scheduling posts"""
        try:
            session = await self.get_database_session()
            
            # Get content piece and validate
            result = await session.execute(
                select(ContentPiece).where(ContentPiece.id == content_piece_id)
            )
            content_piece = result.scalar_one_or_none()
            
            if not content_piece or content_piece.status != "approved_for_posting":
                raise ValueError(f"Content not approved: {content_piece_id}")
                
            # Set default scheduled time
            if not scheduled_time:
                scheduled_time = datetime.utcnow() + timedelta(minutes=5)
                
            # Create post schedule entry
            post_schedule = PostSchedule(
                content_piece_id=content_piece_id,
                social_media_account_id=social_media_account_id,
                scheduled_at=scheduled_time,
                status="pending"
            )
            
            session.add(post_schedule)
            await session.commit()
            
            return {
                "post_schedule_id": str(post_schedule.id),
                "scheduled_at": scheduled_time.isoformat(),
                "status": "pending"
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule post", error=str(e))
            raise