"""
Web server configuration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from internal.handlers import router as handlers_router
from internal.websocket import websocket_endpoint


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Stardew Valley Seed Searcher",
        description="星露谷物语种子搜索器 - Python版本",
        version="1.0.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
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
