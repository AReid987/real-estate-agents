"""
Notification Agent - Handles sending notifications through various channels
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import select
from database.models import Notification, Agent
from agents.agents.base_agent import BaseRealEstateAgent
import structlog

logger = structlog.get_logger()

class NotificationAgent(BaseRealEstateAgent):
    """Agent responsible for managing and sending notifications to users"""
    
    def __init__(self):
        system_message = """
        You are a Notification Agent specialized in managing communication with real estate agents.
        
        Your responsibilities:
        1. Send email notifications about important events
        2. Send push notifications through the web interface
        3. Send SMS notifications (when configured)
        4. Manage notification preferences for each agent
        5. Ensure timely delivery of critical notifications
        
        Notification Types:
        - content_approval_request: New content needs approval
        - approval_processed: Content has been approved/rejected
        - posting_success: Content posted successfully
        - posting_failed: Content posting failed
        - new_listing: New property listing available
        - system_alert: System-level notifications
        
        You ensure agents stay informed about important events and system status.
        """
        
        super().__init__(
            name="NotificationAgent",
            description="Manages and sends notifications through various channels",
            system_message=system_message
        )
        
    async def process_pending_notifications(self) -> Dict[str, Any]:
        """Process all pending notifications"""
        task_id = f"process_notifications_{asyncio.get_event_loop().time()}"
        
        return await self.execute_task(
            task_id,
            self._process_pending_notifications_task
        )
        
    async def _process_pending_notifications_task(self) -> Dict[str, Any]:
        """Internal task for processing pending notifications"""
        try:
            session = await self.get_database_session()
            
            # Get unread notifications from the last 24 hours
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            result = await session.execute(
                select(Notification)
                .where(Notification.is_read == False)
                .where(Notification.created_at >= cutoff_time)
                .order_by(Notification.created_at.desc())
                .limit(50)
            )
            
            notifications = result.scalars().all()
            
            results = {
                "processed": 0,
                "email_sent": 0,
                "push_sent": 0,
                "sms_sent": 0,
                "failed": 0
            }
            
            for notification in notifications:
                try:
                    # Get agent details for notification preferences
                    agent_result = await session.execute(
                        select(Agent).where(Agent.id == notification.agent_id)
                    )
                    agent = agent_result.scalar_one_or_none()
                    
                    if not agent:
                        continue
                        
                    # Process notification based on preferences
                    await self._send_notification(notification, agent, results)
                    results["processed"] += 1
                    
                except Exception as e:
                    logger.error(f"Failed to process notification", 
                               error=str(e), 
                               notification_id=str(notification.id))
                    results["failed"] += 1
                    
            await self.log_action("notifications_processed", results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process pending notifications", error=str(e))
            raise
            
    async def _send_notification(
        self, 
        notification: Notification, 
        agent: Agent, 
        results: Dict[str, Any]
    ):
        """Send notification through appropriate channels"""
        try:
            preferences = agent.notification_preferences or {}
            
            # Send email notification
            if preferences.get("email", True):
                await self._send_email_notification(notification, agent)
                results["email_sent"] += 1
                
            # Send push notification (always enabled for web interface)
            if preferences.get("push", True):
                await self._send_push_notification(notification, agent)
                results["push_sent"] += 1
                
            # Send SMS notification
            if preferences.get("sms", False) and agent.phone:
                await self._send_sms_notification(notification, agent)
                results["sms_sent"] += 1
                
        except Exception as e:
            logger.error(f"Failed to send notification", error=str(e))
            raise
            
    async def _send_email_notification(self, notification: Notification, agent: Agent):
        """Send email notification"""
        try:
            # This would integrate with an email service like SendGrid
            # For now, we'll just log the action
            
            email_content = self._format_email_content(notification, agent)
            
            # TODO: Implement actual email sending
            # await email_service.send_email(
            #     to=agent.email,
            #     subject=email_content["subject"],
            #     body=email_content["body"]
            # )
            
            logger.info(f"Email notification sent", 
                       agent_email=agent.email,
                       notification_type=notification.notification_type,
                       notification_id=str(notification.id))
                       
        except Exception as e:
            logger.error(f"Failed to send email notification", error=str(e))
            raise
            
    async def _send_push_notification(self, notification: Notification, agent: Agent):
        """Send push notification through web interface"""
        try:
            # This would typically use WebSocket or Server-Sent Events
            # to push notifications to the web interface
            
            push_content = {
                "id": str(notification.id),
                "type": notification.notification_type,
                "title": self._get_notification_title(notification.notification_type),
                "message": notification.message_text,
                "timestamp": notification.created_at.isoformat(),
                "agent_id": str(agent.id)
            }
            
            # TODO: Implement actual push notification
            # await websocket_service.send_to_agent(agent.id, push_content)
            
            logger.info(f"Push notification sent", 
                       agent_id=str(agent.id),
                       notification_type=notification.notification_type)
                       
        except Exception as e:
            logger.error(f"Failed to send push notification", error=str(e))
            raise
            
    async def _send_sms_notification(self, notification: Notification, agent: Agent):
        """Send SMS notification"""
        try:
            # This would integrate with an SMS service like Twilio
            
            sms_content = self._format_sms_content(notification, agent)
            
            # TODO: Implement actual SMS sending
            # await sms_service.send_sms(
            #     to=agent.phone,
            #     message=sms_content
            # )
            
            logger.info(f"SMS notification sent", 
                       agent_phone=agent.phone,
                       notification_type=notification.notification_type)
                       
        except Exception as e:
            logger.error(f"Failed to send SMS notification", error=str(e))
            raise
            
    def _format_email_content(self, notification: Notification, agent: Agent) -> Dict[str, str]:
        """Format email content based on notification type"""
        
        title = self._get_notification_title(notification.notification_type)
        
        email_templates = {
            "content_approval_request": {
                "subject": f"Content Approval Required - {agent.name}",
                "body": f"""
                Hi {agent.name},
                
                New marketing content has been generated and requires your approval.
                
                {notification.message_text}
                
                Please log into your dashboard to review and approve the content.
                
                Best regards,
                Real Estate Marketing System
                """
            },
            "posting_success": {
                "subject": f"Content Posted Successfully - {agent.name}",
                "body": f"""
                Hi {agent.name},
                
                Your marketing content has been successfully posted to social media.
                
                {notification.message_text}
                
                You can view the post performance in your dashboard.
                
                Best regards,
                Real Estate Marketing System
                """
            },
            "posting_failed": {
                "subject": f"Content Posting Failed - {agent.name}",
                "body": f"""
                Hi {agent.name},
                
                There was an issue posting your marketing content to social media.
                
                {notification.message_text}
                
                Please check your social media account settings in the dashboard.
                
                Best regards,
                Real Estate Marketing System
                """
            }
        }
        
        template = email_templates.get(notification.notification_type, {
            "subject": f"Notification - {agent.name}",
            "body": f"Hi {agent.name},\n\n{notification.message_text}\n\nBest regards,\nReal Estate Marketing System"
        })
        
        return template
        
    def _format_sms_content(self, notification: Notification, agent: Agent) -> str:
        """Format SMS content (keep it short)"""
        
        sms_templates = {
            "content_approval_request": f"Hi {agent.name}, new content needs approval. Check your dashboard.",
            "posting_success": f"Hi {agent.name}, content posted successfully!",
            "posting_failed": f"Hi {agent.name}, content posting failed. Check dashboard.",
            "new_listing": f"Hi {agent.name}, new listing available for marketing."
        }
        
        return sms_templates.get(
            notification.notification_type, 
            f"Hi {agent.name}, {notification.message_text[:100]}..."
        )
        
    def _get_notification_title(self, notification_type: str) -> str:
        """Get display title for notification type"""
        
        titles = {
            "content_approval_request": "Content Approval Required",
            "approval_processed": "Content Approval Update",
            "posting_success": "Content Posted Successfully",
            "posting_failed": "Content Posting Failed",
            "new_listing": "New Listing Available",
            "system_alert": "System Alert"
        }
        
        return titles.get(notification_type, "Notification")
        
    async def mark_notification_read(self, notification_id: str) -> Dict[str, Any]:
        """Mark a notification as read"""
        try:
            session = await self.get_database_session()
            
            result = await session.execute(
                select(Notification).where(Notification.id == notification_id)
            )
            notification = result.scalar_one_or_none()
            
            if not notification:
                raise ValueError(f"Notification not found: {notification_id}")
                
            notification.is_read = True
            await session.commit()
            
            return {
                "notification_id": notification_id,
                "status": "marked_read"
            }
            
        except Exception as e:
            logger.error(f"Failed to mark notification as read", error=str(e))
            raise