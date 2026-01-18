"""
User Proxy Agent - Handles human-in-the-loop interactions and approvals
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select
from database.models import ContentPiece, ApprovalLog, Notification, Agent
from agents.agents.base_agent import BaseRealEstateAgent
import structlog

logger = structlog.get_logger()

class UserProxyAgent(BaseRealEstateAgent):
    """Agent that handles human-in-the-loop interactions and approval workflows"""
    
    def __init__(self):
        system_message = """
        You are a User Proxy Agent that facilitates communication between AI agents and human users.
        
        Your responsibilities:
        1. Send content to humans for approval
        2. Process approval responses from agents
        3. Create notifications for important events
        4. Track approval history and feedback
        5. Manage the approval workflow states
        
        You ensure that human oversight is maintained in the content creation and posting process.
        """
        
        super().__init__(
            name="UserProxyAgent",
            description="Manages human-in-the-loop interactions and approvals",
            system_message=system_message
        )
        
    async def request_content_approval(
        self,
        content_piece_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """Request approval for generated content from an agent"""
        task_id = f"request_approval_{content_piece_id}"
        
        return await self.execute_task(
            task_id,
            self._request_content_approval_task,
            content_piece_id,
            agent_id
        )
        
    async def _request_content_approval_task(
        self,
        content_piece_id: str,
        agent_id: str
    ) -> Dict[str, Any]:
        """Internal task for requesting content approval"""
        try:
            session = await self.get_database_session()
            
            # Get content piece
            result = await session.execute(
                select(ContentPiece).where(ContentPiece.id == content_piece_id)
            )
            content_piece = result.scalar_one_or_none()
            
            if not content_piece:
                raise ValueError(f"Content piece not found: {content_piece_id}")
                
            # Update content status to pending approval
            content_piece.status = "pending_approval_agent"
            
            # Create notification for the agent
            notification = Notification(
                agent_id=agent_id,
                notification_type="content_approval_request",
                message_text=f"New {content_piece.content_type} content ready for approval",
                related_entity_id=content_piece_id
            )
            
            session.add(notification)
            
            # Log the approval request
            approval_log = ApprovalLog(
                content_piece_id=content_piece_id,
                agent_id=agent_id,
                action_type="requested_revisions",
                feedback="Approval requested from agent"
            )
            
            session.add(approval_log)
            await session.commit()
            
            result = {
                "content_piece_id": content_piece_id,
                "agent_id": agent_id,
                "status": "pending_approval_agent",
                "notification_id": str(notification.id)
            }
            
            await self.log_action("approval_requested", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to request content approval", error=str(e))
            raise
            
    async def process_approval_response(
        self,
        content_piece_id: str,
        agent_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process an approval response from an agent"""
        task_id = f"process_approval_{content_piece_id}"
        
        return await self.execute_task(
            task_id,
            self._process_approval_response_task,
            content_piece_id,
            agent_id,
            approved,
            feedback
        )
        
    async def _process_approval_response_task(
        self,
        content_piece_id: str,
        agent_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Internal task for processing approval responses"""
        try:
            session = await self.get_database_session()
            
            # Get content piece
            result = await session.execute(
                select(ContentPiece).where(ContentPiece.id == content_piece_id)
            )
            content_piece = result.scalar_one_or_none()
            
            if not content_piece:
                raise ValueError(f"Content piece not found: {content_piece_id}")
                
            # Update content status based on approval
            if approved:
                content_piece.status = "approved_for_posting"
                content_piece.last_approved_at = datetime.utcnow()
                action_type = "approved"
                notification_message = f"Content approved and ready for posting"
            else:
                content_piece.status = "rejected"
                action_type = "rejected"
                notification_message = f"Content rejected and needs revision"
                
            # Add feedback if provided
            if feedback:
                content_piece.feedback = feedback
                
            # Log the approval decision
            approval_log = ApprovalLog(
                content_piece_id=content_piece_id,
                agent_id=agent_id,
                action_type=action_type,
                feedback=feedback
            )
            
            session.add(approval_log)
            
            # Create notification about the decision
            notification = Notification(
                agent_id=agent_id,
                notification_type="approval_processed",
                message_text=notification_message,
                related_entity_id=content_piece_id
            )
            
            session.add(notification)
            await session.commit()
            
            result = {
                "content_piece_id": content_piece_id,
                "approved": approved,
                "status": content_piece.status,
                "feedback": feedback,
                "approval_log_id": str(approval_log.id)
            }
            
            await self.log_action("approval_processed", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process approval response", error=str(e))
            raise
            
    async def create_notification(
        self,
        agent_id: str,
        notification_type: str,
        message: str,
        related_entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a notification for an agent"""
        task_id = f"create_notification_{agent_id}"
        
        return await self.execute_task(
            task_id,
            self._create_notification_task,
            agent_id,
            notification_type,
            message,
            related_entity_id
        )
        
    async def _create_notification_task(
        self,
        agent_id: str,
        notification_type: str,
        message: str,
        related_entity_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Internal task for creating notifications"""
        try:
            session = await self.get_database_session()
            
            # Verify agent exists
            result = await session.execute(
                select(Agent).where(Agent.id == agent_id)
            )
            agent = result.scalar_one_or_none()
            
            if not agent:
                raise ValueError(f"Agent not found: {agent_id}")
                
            # Create notification
            notification = Notification(
                agent_id=agent_id,
                notification_type=notification_type,
                message_text=message,
                related_entity_id=related_entity_id
            )
            
            session.add(notification)
            await session.commit()
            
            result = {
                "notification_id": str(notification.id),
                "agent_id": agent_id,
                "type": notification_type,
                "message": message
            }
            
            await self.log_action("notification_created", result)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create notification", error=str(e))
            raise
            
    async def get_pending_approvals(self, agent_id: str) -> Dict[str, Any]:
        """Get pending content approvals for an agent"""
        try:
            session = await self.get_database_session()
            
            # Get content pieces pending approval for this agent
            result = await session.execute(
                select(ContentPiece)
                .where(ContentPiece.agent_id == agent_id)
                .where(ContentPiece.status == "pending_approval_agent")
                .order_by(ContentPiece.created_at.desc())
            )
            
            pending_content = result.scalars().all()
            
            approvals = []
            for content in pending_content:
                approvals.append({
                    "content_piece_id": str(content.id),
                    "content_type": content.content_type,
                    "generated_text": content.generated_text,
                    "created_at": content.created_at.isoformat(),
                    "listing_id": str(content.listing_id) if content.listing_id else None
                })
                
            return {
                "agent_id": agent_id,
                "pending_count": len(approvals),
                "pending_approvals": approvals
            }
            
        except Exception as e:
            logger.error(f"Failed to get pending approvals", error=str(e))
            raise