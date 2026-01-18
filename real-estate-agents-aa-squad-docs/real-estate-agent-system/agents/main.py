"""
Real Estate Agent Marketing System - AG2 Multi-Agent Core
Main entry point for the AG2 agent system
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import structlog
from orchestrator import AgentOrchestrator
from config import settings
from database.connection import init_database

logger = structlog.get_logger()

# Global orchestrator instance
orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global orchestrator
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized")
        
        # Initialize the agent orchestrator
        orchestrator = AgentOrchestrator()
        await orchestrator.initialize()
        logger.info("Agent orchestrator initialized")
        
        yield
        
    except Exception as e:
        logger.error("Failed to initialize application", error=str(e))
        raise
    finally:
        # Cleanup
        if orchestrator:
            await orchestrator.shutdown()
        logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Real Estate Agent Marketing System - AG2 Core",
    description="Multi-Agent system for real estate content marketing and social media management",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ag2-core",
        "version": "1.0.0",
        "agents_active": orchestrator.is_active() if orchestrator else False
    }

@app.post("/agents/generate-content")
async def generate_content(request: dict):
    """Generate content for a specific listing"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    try:
        result = await orchestrator.generate_content(
            listing_id=request.get("listing_id"),
            content_type=request.get("content_type"),
            agent_id=request.get("agent_id")
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Failed to generate content", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/approve-content")
async def approve_content(request: dict):
    """Process content approval from an agent"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    try:
        result = await orchestrator.process_content_approval(
            content_id=request.get("content_id"),
            agent_id=request.get("agent_id"),
            approved=request.get("approved"),
            feedback=request.get("feedback")
        )
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error("Failed to process content approval", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/status")
async def get_agent_status():
    """Get status of all agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    return await orchestrator.get_agent_status()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True if settings.environment == "development" else False,
        log_level="info"
    )