"""
MCP Client - Communicates with GitHub MCP Server via subprocess
"""
import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional
import subprocess

from .models import MCPRequest, MCPResponse

logger = logging.getLogger(__name__)


class MCPClient:
    """Client to communicate with GitHub MCP Server via persistent subprocess"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.toolsets = os.getenv("GITHUB_TOOLSETS", "repos,issues,pull_requests,projects")
        self.binary_path = "/usr/local/bin/github-mcp-server"
        self.process: Optional[asyncio.subprocess.Process] = None
        self.initialized = False
        self.read_task: Optional[asyncio.Task] = None
        self.response_queue = asyncio.Queue()
        self.pending_requests = {}
        
    async def start(self):
        """Start the MCP server subprocess"""
        if self.process is not None:
            logger.warning("MCP Server process already running")
            return
            
        try:
            # Prepare environment
            env = os.environ.copy()
            env["GITHUB_PERSONAL_ACCESS_TOKEN"] = self.github_token
            env["GITHUB_TOOLSETS"] = self.toolsets
            
            # Command to run binary in stdio mode
            cmd = [self.binary_path, "stdio"]
            
            logger.info("Starting GitHub MCP Server subprocess")
            
            # Execute binary with persistent stdin/stdout
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Start background task to read responses
            self.read_task = asyncio.create_task(self._read_responses())
            
            logger.info("GitHub MCP Server subprocess started successfully")
            
            # Initialize MCP session automatically
            await self._initialize_session()
            
        except Exception as e:
            logger.error(f"Failed to start MCP Server subprocess: {e}")
            raise
    
    async def _initialize_session(self):
        """Initialize the MCP session (handshake)"""
        try:
            logger.info("Initializing MCP session")
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "github-mcp-server-addon", "version": "1.0.0"}
                },
                "id": "init-1"
            }
            
            future = asyncio.Future()
            self.pending_requests["init-1"] = future
            
            request_data = json.dumps(init_request) + '\n'
            self.process.stdin.write(request_data.encode())
            await self.process.stdin.drain()
            
            # Wait for initialize response
            init_response = await asyncio.wait_for(future, timeout=10.0)
            logger.info("MCP initialize successful")
            
            # Send initialized notification (no ID needed for notifications)
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            notif_data = json.dumps(initialized_notification) + '\n'
            self.process.stdin.write(notif_data.encode())
            await self.process.stdin.drain()
            
            await asyncio.sleep(0.5)  # Give server time to process
            
            self.initialized = True
            logger.info("MCP session initialized and ready")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP session: {e}")
            raise
    
    async def _read_responses(self):
        """Background task to read responses from stdout"""
        try:
            while self.process and self.process.stdout:
                line = await self.process.stdout.readline()
                if not line:
                    break
                    
                try:
                    response_data = json.loads(line.decode().strip())
                    response_id = response_data.get("id")
                    
                    if response_id is None:
                        # This is a notification (no ID), log and continue
                        method = response_data.get("method", "unknown")
                        logger.debug(f"Received MCP notification: {method}")
                        continue
                    
                    if response_id in self.pending_requests:
                        # Resolve pending request
                        future = self.pending_requests.pop(response_id)
                        future.set_result(response_data)
                    else:
                        logger.warning(f"Received response for unknown request ID: {response_id}")
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}")
                except Exception as e:
                    logger.error(f"Error processing response: {e}")
                    
        except Exception as e:
            logger.error(f"Error in read_responses task: {e}")
        finally:
            logger.info("Response reader task ended")
        
    async def execute(self, request: MCPRequest) -> MCPResponse:
        """
        Execute MCP command via GitHub MCP Server
        
        Args:
            request: MCP request object
            
        Returns:
            MCPResponse with result or error
        """
        # Ensure server is started
        if self.process is None:
            await self.start()
            
        try:
            # Prepare JSON-RPC request
            json_rpc_request = {
                "jsonrpc": request.jsonrpc,
                "method": request.method,
                "params": request.params or {},
                "id": request.id
            }
            
            logger.info(f"Sending MCP request: {request.method}")
            logger.debug(f"Request: {json_rpc_request}")
            
            # Create future for response
            future = asyncio.Future()
            self.pending_requests[request.id] = future
            
            # Send request to MCP server via stdin
            request_data = json.dumps(json_rpc_request) + '\n'
            self.process.stdin.write(request_data.encode())
            await self.process.stdin.drain()
            
            # Wait for response with timeout
            try:
                response_data = await asyncio.wait_for(future, timeout=30.0)
                
                # Handle JSON-RPC error response
                if "error" in response_data:
                    return MCPResponse(
                        jsonrpc="2.0",
                        id=request.id,
                        error=response_data["error"]
                    )
                
                # Return successful response
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result=response_data.get("result", response_data)
                )
                
            except asyncio.TimeoutError:
                # Clean up pending request
                self.pending_requests.pop(request.id, None)
                logger.error("MCP request timed out")
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    error={
                        "code": -32001,
                        "message": "Request timeout (30s)"
                    }
                )
                
        except Exception as e:
            logger.error(f"Unexpected error executing MCP command: {e}", exc_info=True)
            return MCPResponse(
                jsonrpc="2.0",
                id=request.id,
                error={
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            )
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.read_task:
                self.read_task.cancel()
                
            if self.process and self.process.returncode is None:
                logger.info("Terminating MCP Server subprocess")
                self.process.terminate()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("MCP Server didn't terminate, killing")
                    self.process.kill()
                    
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        finally:
            logger.info("MCP Client cleanup completed")
