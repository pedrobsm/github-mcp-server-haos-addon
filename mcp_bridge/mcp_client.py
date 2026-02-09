"""
MCP Client - Communicates with GitHub MCP Server via subprocess
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
    """Client to communicate with GitHub MCP Server via subprocess"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        self.toolsets = os.getenv("GITHUB_TOOLSETS", "repos,issues,pull_requests,projects")
        self.binary_path = "/usr/local/bin/github-mcp-server"
        
    async def execute(self, request: MCPRequest) -> MCPResponse:
        """
        Execute MCP command by running GitHub MCP Server binary
        
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
            
            # Prepare environment
            env = os.environ.copy()
            env["GITHUB_PERSONAL_ACCESS_TOKEN"] = self.github_token
            env["GITHUB_TOOLSETS"] = self.toolsets
            
            # Command to run binary in stdio mode
            cmd = [self.binary_path, "stdio"]
            
            logger.debug(f"Running GitHub MCP Server (token hidden)")
            logger.debug(f"JSON-RPC request: {json_rpc_request}")
            
            # Execute binary with MCP request via stdin
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
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
                logger.error(f"GitHub MCP Server process failed: {error_msg}")
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
