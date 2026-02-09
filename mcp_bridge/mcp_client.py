"""
MCP Client - Communicates with GitHub MCP Server via Docker
"""
import os
import json
import asyncio
import logging
from typing import Dict, Any
import subprocess

from models import MCPRequest, MCPResponse

logger = logging.getLogger(__name__)


class MCPClient:
    """Client to communicate with GitHub MCP Server via Docker subprocess"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.toolsets = os.getenv("GITHUB_TOOLSETS", "repos,issues,pull_requests,projects")
        self.image = "ghcr.io/github/github-mcp-server:0.30.3"
        
    async def execute(self, request: MCPRequest) -> MCPResponse:
        """
        Execute MCP command by running GitHub MCP Server in Docker container
        
        Args:
            request: MCP request object
            
        Returns:
            MCPResponse with result or error
        """
        try:
            # Prepare JSON-RPC request
            json_rpc_request = {
                "jsonrpc": request.jsonrpc,
                "method": request.method,
                "params": request.params or {},
                "id": request.id
            }
            
            # Prepare Docker command
            docker_cmd = [
                "docker", "run",
                "-i",  # Interactive for stdin/stdout
                "--rm",  # Remove container after execution
                "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={self.github_token}",
                "-e", f"GITHUB_TOOLSETS={self.toolsets}",
                self.image
            ]
            
            logger.debug(f"Running Docker command (token hidden)")
            logger.debug(f"JSON-RPC request: {json_rpc_request}")
            
            # Execute Docker container with MCP request via stdin
            process = await asyncio.create_subprocess_exec(
                *docker_cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Send request to MCP server via stdin
            request_data = json.dumps(json_rpc_request).encode() + b'\n'
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=request_data),
                timeout=30.0  # 30 second timeout
            )
            
            # Check for errors
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Docker process failed: {error_msg}")
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    error={
                        "code": -32603,
                        "message": f"MCP server error: {error_msg}"
                    }
                )
            
            # Parse response
            response_text = stdout.decode().strip()
            logger.debug(f"MCP server raw response: {response_text}")
            
            if not response_text:
                logger.warning("Empty response from MCP server")
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    result={"status": "no_response"}
                )
            
            # Parse JSON response
            try:
                response_data = json.loads(response_text)
                
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
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse MCP response: {e}")
                logger.error(f"Response text: {response_text}")
                return MCPResponse(
                    jsonrpc="2.0",
                    id=request.id,
                    error={
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                )
                
        except asyncio.TimeoutError:
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
        logger.info("MCP Client cleanup completed")
