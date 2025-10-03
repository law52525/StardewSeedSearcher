#!/usr/bin/env python3
"""
Stardew Valley Seed Searcher - Python Version
Main application entry point
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from internal.server import create_app
from internal.websocket import websocket_endpoint

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stardew-seed-searcher.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("==========================================")
    logger.info("  星露谷种子搜索器 - Web 服务启动")
    logger.info("==========================================")
    logger.info("")
    logger.info("服务器地址: http://localhost:5000")
    logger.info("WebSocket: ws://localhost:5000/ws")
    logger.info("")
    logger.info("请打开 index.html 开始使用")
    logger.info("按 Ctrl+C 停止服务器")
    logger.info("")
    yield
    logger.info("服务器正在关闭...")

def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Stardew Valley Seed Searcher",
        description="星露谷物语种子搜索器 - Python版本",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    from internal.handlers import router as handlers_router
    app.include_router(handlers_router)
    
    # WebSocket endpoint
    app.add_websocket_route("/ws", websocket_endpoint)
    
    # Serve static files (for index.html)
    app.mount("/static", StaticFiles(directory="."), name="static")
    
    # Root endpoint - serve index.html
    @app.get("/", response_class=HTMLResponse)
    async def read_root():
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    
    return app

# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", "5000"))
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
