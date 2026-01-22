"""
HTTP API wrapper for Building Code MCP Server.
For hosting on Railway/Render/Vercel.
"""

import os
import sys
from pathlib import Path

# Fix path for Vercel
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict
import uvicorn

from src.mcp_server import BuildingCodeMCP

# Maps directory (absolute path for Vercel)
MAPS_DIR = str(BASE_DIR / "maps")


# MCP Tool definitions
MCP_TOOLS = [
    {
        "name": "list_codes",
        "description": "List all available Canadian building codes with section counts",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "search_code",
        "description": "Search for building code sections by keywords (e.g., 'fire separation', 'stair width')",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "code": {"type": "string", "description": "Specific code to search (e.g., 'NBC', 'OBC', 'OFC')"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_section",
        "description": "Get details of a specific section by ID",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section_id": {"type": "string", "description": "Section ID (e.g., '9.9.4.1')"},
                "code": {"type": "string", "description": "Code name (optional)"}
            },
            "required": ["section_id"]
        }
    },
    {
        "name": "get_hierarchy",
        "description": "Get parent, children, and sibling sections for navigation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "section_id": {"type": "string", "description": "Section ID"},
                "code": {"type": "string", "description": "Code name (optional)"}
            },
            "required": ["section_id"]
        }
    },
    {
        "name": "verify_section",
        "description": "Verify that a section ID exists and get a formal citation",
        "inputSchema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Section ID to verify"},
                "code": {"type": "string", "description": "Code name"}
            },
            "required": ["id", "code"]
        }
    },
    {
        "name": "get_applicable_code",
        "description": "Determine which building codes apply to a specific Canadian location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Canadian location (city or province)"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_table",
        "description": "Get a specific table from the building code",
        "inputSchema": {
            "type": "object",
            "properties": {
                "table_id": {"type": "string", "description": "Table ID (e.g., '4.1.5.3', 'Table-9.10.14.4')"},
                "code": {"type": "string", "description": "Code name (optional)"}
            },
            "required": ["table_id"]
        }
    },
    {
        "name": "set_pdf_path",
        "description": "[LOCAL ONLY] Connect your PDF for text extraction. NOT available in hosted API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code name"},
                "path": {"type": "string", "description": "Path to PDF file"}
            },
            "required": ["code", "path"]
        }
    },
    {
        "name": "get_page",
        "description": "[LOCAL ONLY] Get full text of a specific page. Requires PDF connected.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code name"},
                "page": {"type": "integer", "description": "Page number"}
            },
            "required": ["code", "page"]
        }
    },
    {
        "name": "get_pages",
        "description": "[LOCAL ONLY] Get text from a range of pages (max 5). Requires PDF connected.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Code name"},
                "start_page": {"type": "integer", "description": "First page"},
                "end_page": {"type": "integer", "description": "Last page"}
            },
            "required": ["code", "start_page", "end_page"]
        }
    }
]

app = FastAPI(
    title="Canadian Building Code API",
    description="Search 20,000+ sections across 13 Canadian building codes",
    version="1.0.0"
)

# CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP
mcp = BuildingCodeMCP(MAPS_DIR)


class SearchRequest(BaseModel):
    query: str
    code: Optional[str] = None
    limit: Optional[int] = 20


class SectionRequest(BaseModel):
    section_id: str
    code: Optional[str] = None


@app.get("/")
def root():
    return {
        "name": "Canadian Building Code API",
        "version": "1.0.0",
        "endpoints": ["/codes", "/search", "/section/{id}"]
    }


@app.get("/health")
def health():
    return {"status": "ok"}


# ============== MCP JSON-RPC Protocol ==============

def handle_mcp_request(method: str, params: Dict = None, req_id: Any = None) -> Dict:
    """Handle MCP JSON-RPC methods."""
    params = params or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "canada-building-code-mcp",
                    "version": "1.0.0"
                }
            }
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": MCP_TOOLS}
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        try:
            if tool_name == "list_codes":
                result = mcp.list_codes()
            elif tool_name == "search_code":
                result = mcp.search_code(
                    arguments.get("query", ""),
                    arguments.get("code")
                )
            elif tool_name == "get_section":
                result = mcp.get_section(
                    arguments.get("section_id", ""),
                    arguments.get("code")
                )
            elif tool_name == "get_hierarchy":
                result = mcp.get_hierarchy(
                    arguments.get("section_id", ""),
                    arguments.get("code")
                )
            elif tool_name == "verify_section":
                result = mcp.verify_section(
                    arguments.get("id", ""),
                    arguments.get("code", "")
                )
            elif tool_name == "get_applicable_code":
                result = mcp.get_applicable_code(
                    arguments.get("location", "")
                )
            elif tool_name == "get_table":
                result = mcp.get_table(
                    arguments.get("table_id", ""),
                    arguments.get("code")
                )
            elif tool_name in ("set_pdf_path", "get_page", "get_pages"):
                # Not available in hosted mode
                result = {
                    "error": f"{tool_name} is not available in hosted API mode",
                    "reason": "Hosted servers cannot access your local PDF files",
                    "solution": "Run the MCP server locally to use BYOD (Bring Your Own Document) mode",
                    "local_setup": "pip install building-code-mcp && building-code-mcp"
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                }

            import json
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result)}],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                    "isError": True
                }
            }

    elif method == "notifications/initialized":
        return None

    else:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }


@app.post("/")
async def mcp_jsonrpc(request: Request):
    """MCP JSON-RPC endpoint."""
    try:
        body = await request.json()
    except:
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"}
        })

    if isinstance(body, list):
        responses = []
        for req in body:
            resp = handle_mcp_request(req.get("method"), req.get("params"), req.get("id"))
            if resp:
                responses.append(resp)
        return JSONResponse(responses)
    else:
        resp = handle_mcp_request(body.get("method"), body.get("params"), body.get("id"))
        if resp:
            return JSONResponse(resp)
        return JSONResponse({"jsonrpc": "2.0", "result": "ok"})


@app.get("/.well-known/mcp/server-card.json")
def server_card():
    """Smithery MCP server card for discovery."""
    return {
        "name": "canada-building-code-mcp",
        "description": "Search 20,000+ sections across 13 Canadian building codes",
        "version": "1.0.0",
        "tools": [
            {
                "name": "list_codes",
                "description": "List all available Canadian building codes with section counts"
            },
            {
                "name": "search_code",
                "description": "Search for building code sections by keywords",
                "parameters": {
                    "query": {"type": "string", "description": "Search query"},
                    "code": {"type": "string", "description": "Code to search (optional)"}
                }
            },
            {
                "name": "get_section",
                "description": "Get details of a specific section by ID",
                "parameters": {
                    "section_id": {"type": "string", "description": "Section ID"},
                    "code": {"type": "string", "description": "Code name (optional)"}
                }
            },
            {
                "name": "get_hierarchy",
                "description": "Get parent, children, and sibling sections",
                "parameters": {
                    "section_id": {"type": "string", "description": "Section ID"},
                    "code": {"type": "string", "description": "Code name (optional)"}
                }
            }
        ]
    }


@app.get("/codes")
def list_codes():
    """List all available building codes."""
    return mcp.list_codes()


@app.post("/search")
def search(request: SearchRequest):
    """Search for building code sections."""
    result = mcp.search_code(request.query, request.code)
    if request.limit:
        result["results"] = result["results"][:request.limit]
    return result


@app.get("/search/{query}")
def search_get(query: str, code: Optional[str] = None, limit: int = 20):
    """Search via GET request."""
    result = mcp.search_code(query, code)
    result["results"] = result["results"][:limit]
    return result


@app.get("/section/{section_id}")
def get_section(section_id: str, code: Optional[str] = None):
    """Get a specific section by ID."""
    result = mcp.get_section(section_id, code)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@app.get("/hierarchy/{section_id}")
def get_hierarchy(section_id: str, code: Optional[str] = None):
    """Get section hierarchy (parent, children, siblings)."""
    return mcp.get_hierarchy(section_id, code)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
