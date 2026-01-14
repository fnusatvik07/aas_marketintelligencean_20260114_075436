# ui_user_5f126afd/main.py
"""
Market Intelligence Analyst - Auto-generated FastAPI service
Role: Competitive Intelligence and Market Research Specialist
"""
import asyncio
import json
import os
import datetime
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import Message, AssistantMessage, ResultMessage, TextBlock, ToolUseBlock, ToolResultBlock
from dotenv import load_dotenv
from typing import AsyncGenerator

load_dotenv()

app = FastAPI(
    title="Market Intelligence Analyst",
    description="Competitive Intelligence and Market Research Specialist",
    version="1.0.0"
)

# CORS Configuration - Allow frontend connections
CORS_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:8080",  # Agent as a Service UI
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    # Allow frontend ports (backend + 1, 2, 3)
    f"http://localhost:8050",
    f"http://localhost:8051", 
    f"http://localhost:8052",
    f"http://127.0.0.1:8050",
    f"http://127.0.0.1:8051",
    f"http://127.0.0.1:8052"
]

# For development, also allow all localhost origins
import re
DEV_ORIGINS = [f"http://localhost:{port}" for port in range(3000, 9000)] +               [f"http://127.0.0.1:{port}" for port in range(3000, 9000)]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS + DEV_ORIGINS if os.getenv("ENVIRONMENT") != "production" else CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class QueryRequest(BaseModel):
    prompt: str
    max_turns: int = 20

class QueryResponse(BaseModel):
    status: str
    response: str
    usage: dict = None
    agent_info: dict = None

class StreamEvent(BaseModel):
    type: str  # "progress", "tool_use", "response", "complete", "error"
    data: dict
    timestamp: str

# Agent configuration
AGENT_CONFIG = {
    "name": "Market Intelligence Analyst",
    "role": "Competitive Intelligence and Market Research Specialist",
    "tools": ['WebSearch', 'WebFetch', 'Read', 'Write', 'Bash', 'TodoWrite', 'AskUserQuestion'],
    "system_prompt": """You are a Market Intelligence Analyst specializing in competitive research and market trend analysis. Your primary responsibility is to gather, analyze, and synthesize market intelligence into actionable weekly reports.

Your core competencies include:
- Conducting comprehensive web research to identify competitor activities, product launches, pricing changes, and strategic moves
- Monitoring industry news, market trends, and emerging patterns across multiple sources
- Analyzing competitor websites, press releases, social media, and public financial disclosures
- Processing and structuring raw data into meaningful insights
- Identifying market opportunities, threats, and strategic implications
- Generating clear, concise weekly reports with executive summaries and detailed findings

Your workflow:
1. Ask clarifying questions about specific competitors, industries, or metrics to track
2. Systematically search for relevant information across web sources
3. Fetch and analyze content from competitor websites and industry publications
4. Process and organize collected data into structured formats
5. Identify trends, patterns, and notable changes from previous periods
6. Create comprehensive reports with key findings, visualizations, and recommendations
7. Maintain task lists to track research priorities and report deadlines

Communication style:
- Analytical and data-driven in your assessments
- Objective and balanced in presenting findings
- Clear and concise in written reports
- Proactive in asking for clarification on research scope and priorities

Always cite sources, timestamp your findings, and distinguish between verified facts and analytical interpretations. Focus on actionable insights that support strategic decision-making.""",
    "permission_mode": "default"
}

@app.get("/")
async def root():
    return {
        "message": "Welcome to Market Intelligence Analyst",
        "role": "Competitive Intelligence and Market Research Specialist",
        "agent_id": "ui_user_5f126afd",
        "endpoints": [
            "/query - POST: Send a task to the agent",
            "/stream - POST: Stream agent progress in real-time",
            "/info - GET: Get agent information",
            "/health - GET: Check service health"
        ]
    }

@app.get("/info")
async def get_agent_info():
    return {
        "agent_id": "ui_user_5f126afd",
        "name": AGENT_CONFIG["name"],
        "role": AGENT_CONFIG["role"],
        "tools": AGENT_CONFIG["tools"],
        "status": "active",
        "features": ["streaming", "real-time_progress"]
    }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests for all paths"""
    return {"message": "CORS preflight OK"}

@app.get("/frontend-info")
async def get_frontend_info():
    """Get frontend connection information"""
    return {
        "backend_url": f"http://localhost:8049",
        "frontend_url": f"http://localhost:8050",
        "cors_enabled": True,
        "connection_test": "ready"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with CORS info"""
    return {
        "status": "healthy", 
        "agent": "Market Intelligence Analyst",
        "role": "Competitive Intelligence and Market Research Specialist",
        "cors_enabled": True,
        "backend_port": 8049,
        "frontend_port": 8050,
        "timestamp": datetime.datetime.now().isoformat()
    }

@app.get("/files")
async def list_files():
    """
    List all generated files in the agent directory
    """
    try:
        files_dir = Path("./generated_files")
        if not files_dir.exists():
            files_dir.mkdir(exist_ok=True)
            
        files = []
        for file_path in files_dir.glob("*"):
            if file_path.is_file():
                files.append({
                    "filename": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return {"files": files, "count": len(files)}
    except Exception as e:
        return {"files": [], "count": 0, "error": str(e)}

@app.get("/files/{filename}")
async def download_file(filename: str):
    """
    Download a specific generated file
    """
    try:
        file_path = Path("./generated_files") / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def stream_agent_progress(request: QueryRequest) -> AsyncGenerator[str, None]:
    """
    Stream agent progress in real-time
    """
    def create_event(event_type: str, data: dict) -> str:
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.datetime.now().isoformat()
        }
        return f"data: {json.dumps(event)}\n\n"
    
    try:
        # Send initial event
        yield create_event("progress", {
            "message": "[AGENT] Starting Market Intelligence Analyst...",
            "agent": AGENT_CONFIG["name"],
            "status": "initializing"
        })
        
        # Create Claude Agent SDK options
        options = ClaudeAgentOptions(
            allowed_tools=AGENT_CONFIG["tools"],
            system_prompt=AGENT_CONFIG["system_prompt"],
            permission_mode=AGENT_CONFIG["permission_mode"],
            max_turns=request.max_turns,
        )
        
        yield create_event("progress", {
            "message": "[PROCESSING] Processing your request...",
            "status": "processing"
        })
        
        # Execute the query and stream progress
        response_parts = []
        usage_info = None
        
        async for message in query(prompt=request.prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)
                        # Stream partial response
                        yield create_event("response", {
                            "content": block.text,
                            "partial": True,
                            "message": "[THINKING] Agent thinking..."
                        })
                    elif isinstance(block, ToolUseBlock):
                        # Stream tool usage
                        yield create_event("tool_use", {
                            "tool": block.name,
                            "input": block.input,
                            "message": f"[TOOL] Using {block.name} tool...",
                            "status": "executing"
                        })
            elif isinstance(message, ResultMessage):
                usage_info = {
                    "duration_ms": message.duration_ms,
                    "total_cost_usd": message.total_cost_usd,
                    "num_turns": message.num_turns,
                    "session_id": message.session_id
                }
                break
        
        full_response = "\n".join(response_parts) if response_parts else "No response received"
        
        # Send completion event
        yield create_event("complete", {
            "response": full_response,
            "usage": usage_info or {},
            "status": "completed",
            "message": "[SUCCESS] Task completed successfully!",
            "agent_info": {
                "name": AGENT_CONFIG["name"],
                "role": AGENT_CONFIG["role"]
            }
        })
        
    except Exception as e:
        yield create_event("error", {
            "error": str(e),
            "message": f"[ERROR] Error: {str(e)}",
            "status": "failed"
        })

@app.post("/stream")
async def stream_query(request: QueryRequest):
    """
    Stream agent progress in real-time using Server-Sent Events (SSE)
    """
    return StreamingResponse(
        stream_agent_progress(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Send a query/task to the Market Intelligence Analyst (non-streaming)
    """
    try:
        # Create Claude Agent SDK options
        options = ClaudeAgentOptions(
            allowed_tools=AGENT_CONFIG["tools"],
            system_prompt=AGENT_CONFIG["system_prompt"],
            permission_mode=AGENT_CONFIG["permission_mode"],
            max_turns=request.max_turns,
        )
        
        # Execute the query
        response_parts = []
        usage_info = None
        
        async for message in query(prompt=request.prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        response_parts.append(block.text)
            elif isinstance(message, ResultMessage):
                usage_info = {
                    "duration_ms": message.duration_ms,
                    "total_cost_usd": message.total_cost_usd,
                    "num_turns": message.num_turns,
                    "session_id": message.session_id
                }
                break
        
        full_response = "\n".join(response_parts) if response_parts else "No response received"
        
        return QueryResponse(
            status="success",
            response=full_response,
            usage=usage_info or {},
            agent_info={
                "name": AGENT_CONFIG["name"],
                "role": AGENT_CONFIG["role"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    print(f"[INFO] Market Intelligence Analyst Backend Starting...")
    print(f"[BACKEND] Backend URL: http://localhost:8049")
    print(f"[FRONTEND] Frontend URL: http://localhost:8050")  
    print(f"[CORS] CORS: Enabled for frontend connections")
    print(f"[DOCS] API Docs: http://localhost:8049/docs")
    print(f"[HEALTH] Health: http://localhost:8049/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8049)
