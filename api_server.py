"""
HTTP API wrapper for Building Code MCP Server.
For hosting on Railway/Render/Vercel.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from src.mcp_server import BuildingCodeMCP

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
mcp = BuildingCodeMCP("maps")


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
