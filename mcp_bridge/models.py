"""
Pydantic models for MCP requests and responses
"""
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """MCP JSON-RPC request model"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(..., description="MCP method name")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")
    id: Union[int, str] = Field(default=1, description="Request ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
        }


class MCPResponse(BaseModel):
    """MCP JSON-RPC response model"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Union[int, str] = Field(..., description="Request ID")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Success result")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "tools": []
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Health status: healthy, degraded, or unhealthy")
    docker_accessible: bool = Field(..., description="Whether Docker is accessible")
    version: str = Field(..., description="Add-on version")
    error: Optional[str] = Field(default=None, description="Error message if unhealthy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "docker_accessible": True,
                "version": "1.0.0"
            }
        }
