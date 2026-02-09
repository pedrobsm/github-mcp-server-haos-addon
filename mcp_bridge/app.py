"""
FastAPI wrapper for GitHub MCP Server
Converts HTTP requests to MCP stdio protocol
"""
import os
import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .models import MCPRequest, MCPResponse, HealthResponse
from .mcp_client import MCPClient

# Configure logging
log_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GitHub MCP Server",
    description="HTTP wrapper for GitHub Model Context Protocol Server",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for VSCode remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for VSCode remote access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP client
mcp_client = MCPClient()


@app.on_event("startup")
async def startup_event():
    """Initialize MCP client on startup"""
    logger.info("Starting GitHub MCP Server HTTP wrapper")
    logger.info(f"Log level: {log_level}")
    
    # Validate environment
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        logger.error("GITHUB_PERSONAL_ACCESS_TOKEN not set!")
        raise RuntimeError("GitHub token is required")
    
    toolsets = os.getenv("GITHUB_TOOLSETS", "repos,issues,pull_requests,projects")
    logger.info(f"Configured toolsets: {toolsets}")
    logger.info(f"Token: ghp_***{token[-4:]}")
    logger.info("MCP Server ready to accept connections")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down GitHub MCP Server")
    await mcp_client.cleanup()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns status of the MCP server
    """
    try:
        # Check if Docker is accessible
        import subprocess
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            timeout=5
        )
        docker_ok = result.returncode == 0
        
        return HealthResponse(
            status="healthy" if docker_ok else "degraded",
            docker_accessible=docker_ok,
            version="1.0.0"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status="unhealthy",
            docker_accessible=False,
            version="1.0.0",
            error=str(e)
        )


@app.post("/mcp/execute", response_model=MCPResponse)
async def execute_mcp_command(request: MCPRequest):
    """
    Execute MCP command via GitHub MCP Server
    
    Accepts JSON-RPC formatted MCP requests and returns responses
    """
    try:
        logger.info(f"Executing MCP command: {request.method}")
        logger.debug(f"Request params: {request.params}")
        
        # Execute command via MCP client
        response = await mcp_client.execute(request)
        
        logger.debug(f"MCP response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error executing MCP command: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"MCP execution failed: {str(e)}"
        )


@app.post("/mcp/initialize")
async def initialize_session(request: Request):
    """
    Initialize MCP session
    Compatible with MCP protocol initialization
    """
    try:
        body = await request.json()
        logger.info("Initializing MCP session")
        
        # Forward to MCP server
        mcp_request = MCPRequest(
            jsonrpc="2.0",
            method="initialize",
            params=body.get("params", {}),
            id=body.get("id", 1)
        )
        
        response = await mcp_client.execute(mcp_request)
        return JSONResponse(content=response.dict())
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "GitHub MCP Server",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "execute": "/mcp/execute",
            "initialize": "/mcp/initialize",
            "docs": "/docs"
        },
        "mcp_version": "0.30.3"
    }


if __name__ == "__main__":
    port = int(os.getenv("MCP_PORT", 8080))
    logger.info(f"Starting server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level=log_level.lower(),
        access_log=True
    )
