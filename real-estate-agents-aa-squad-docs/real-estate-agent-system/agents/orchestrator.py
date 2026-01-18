"""
Agent Orchestrator - Coordinates all agents in the system
"""

import asyncio
from typing import Dict, Any, List, Optional
from agents.agents.listing_agent import ListingAgent
from agents.agents.content_agent import ContentAgent
from agents.agents.social_media_agent import SocialMediaAgent
from agents.agents.user_proxy_agent import UserProxyAgent
from agents.agents.notification_agent import NotificationAgent
import structlog

logger = structlog.get_logger()

class AgentOrchestrator:
    """Orchestrates all agents in the real estate marketing system"""
    
    def __init__(self):
        self.agents = {}
        self._is_active = False
        self._background_tasks = []
        
    async def initialize(self):
        """Initialize all agents"""
        try:
            # Initialize all agents
            self.agents = {
                "listing": ListingAgent(),
                "content": ContentAgent(),
                "social_media": SocialMediaAgent(),
                "user_proxy": UserProxyAgent(),
                "notification": NotificationAgent()
            }
            
            # Initialize each agent
            for agent_name, agent in self.agents.items():
                await agent.initialize()
                logger.info(f"Agent initialized", agent=agent_name)
                
            self._is_active = True
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("Agent orchestrator initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize agent orchestrator", error=str(e))
            raise
            
    async def shutdown(self):
        """Shutdown all agents and background tasks"""
        try:
            self._is_active = False
            
            # Cancel background tasks
            for task in self._background_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
            self._background_tasks.clear()
            
            # Shutdown all agents
            for agent_name, agent in self.agents.items():
                await agent.shutdown()
                logger.info(f"Agent shutdown", agent=agent_name)
                
            logger.info("Agent orchestrator shutdown complete")
            
        except Exception as e:
            logger.error("Failed to shutdown agent orchestrator", error=str(e))
            
    def is_active(self) -> bool:
        """Check if orchestrator is active"""
        return self._is_active
        
    async def _start_background_tasks(self):
        """Start background tasks for periodic operations"""
        try:
            # Task to process scheduled posts every minute
            self._background_tasks.append(
                asyncio.create_task(self._periodic_post_processing())
            )
            
            # Task to process notifications every 30 seconds
            self._background_tasks.append(
                asyncio.create_task(self._periodic_notification_processing())
            )
            
            # Task to scrape new listings every 30 minutes
            self._background_tasks.append(
                asyncio.create_task(self._periodic_listing_scraping())
            )
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error("Failed to start background tasks", error=str(e))
            
    async def _periodic_post_processing(self):
        """Periodically process scheduled posts"""
        while self._is_active:
            try:
                await asyncio.sleep(60)  # Every minute
                if self._is_active:
                    await self.agents["social_media"].process_scheduled_posts()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in periodic post processing", error=str(e))
                await asyncio.sleep(5)  # Brief delay before retrying
                
    async def _periodic_notification_processing(self):
        """Periodically process pending notifications"""
        while self._is_active:
            try:
                await asyncio.sleep(30)  # Every 30 seconds
                if self._is_active:
                    await self.agents["notification"].process_pending_notifications()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in periodic notification processing", error=str(e))
                await asyncio.sleep(5)
                
    async def _periodic_listing_scraping(self):
        """Periodically scrape new listings"""
        while self._is_active:
            try:
                await asyncio.sleep(1800)  # Every 30 minutes
                if self._is_active:
                    await self.agents["listing"].process_new_listings()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error in periodic listing scraping", error=str(e))
                await asyncio.sleep(60)  # Wait a minute before retrying
                
    async def process_new_listing(self, listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a new listing through the agent system"""
        try:
            logger.info("Processing new listing", listing_id=listing_data.get("id"))
            
            # This would trigger content generation for the new listing
            result = {
                "status": "processed",
                "listing_id": listing_data.get("id"),
                "message": "New listing processed successfully"
            }
            
            return result
            
        except Exception as e:
            logger.error("Failed to process new listing", error=str(e))
            raise
            
    async def process_content_approval(
        self,
        content_id: str,
        agent_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process content approval from an agent"""
        try:
            logger.info("Processing content approval", 
                       content_id=content_id, 
                       approved=approved)
            
            # Use user proxy agent to handle the approval
            result = await self.agents["user_proxy"].process_approval_response(
                content_id, agent_id, approved, feedback
            )
            
            # If approved, schedule for posting
            if approved and result.get("status") == "approved_for_posting":
                # This would trigger scheduling logic
                logger.info("Content approved, ready for scheduling", content_id=content_id)
                
            return result
            
        except Exception as e:
            logger.error("Failed to process content approval", error=str(e))
            raise
            
    async def generate_content(
        self,
        listing_id: str,
        content_type: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """Generate content for a specific listing"""
        try:
            logger.info("Generating content", 
                       listing_id=listing_id, 
                       content_type=content_type)
            
            # Use content agent to generate content
            result = await self.agents["content"].generate_content(
                listing_id, content_type, agent_id
            )
            
            # Request approval from user proxy
            if result.get("content_piece_id"):
                await self.agents["user_proxy"].request_content_approval(
                    result["content_piece_id"], agent_id
                )
                
            return result
            
        except Exception as e:
            logger.error("Failed to generate content", error=str(e))
            raise
            
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        try:
            status = {
                "orchestrator_active": self._is_active,
                "background_tasks": len(self._background_tasks),
                "agents": {}
            }
            
            for agent_name, agent in self.agents.items():
                status["agents"][agent_name] = await agent.get_status()
                
            return status
            
        except Exception as e:
            logger.error("Failed to get agent status", error=str(e))
            raise
            
    async def schedule_content_posting(
        self,
        content_piece_id: str,
        social_media_account_id: str,
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Schedule content for posting to social media"""
        try:
            from datetime import datetime
            
            scheduled_dt = None
            if scheduled_time:
                scheduled_dt = datetime.fromisoformat(scheduled_time)
                
            result = await self.agents["social_media"].schedule_post(
                content_piece_id,
                social_media_account_id,
                scheduled_dt
            )
            
            return result
            
        except Exception as e:
            logger.error("Failed to schedule content posting", error=str(e))
            raise
            
    async def get_pending_approvals(self, agent_id: str) -> Dict[str, Any]:
        """Get pending content approvals for an agent"""
        try:
            result = await self.agents["user_proxy"].get_pending_approvals(agent_id)
            return result
            
        except Exception as e:
            logger.error("Failed to get pending approvals", error=str(e))
            raise
            
    async def create_notification(
        self,
        agent_id: str,
        notification_type: str,
        message: str,
        related_entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a notification for an agent"""
        try:
            result = await self.agents["user_proxy"].create_notification(
                agent_id, notification_type, message, related_entity_id
            )
            return result
            
        except Exception as e:
            logger.error("Failed to create notification", error=str(e))
            raise