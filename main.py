"""Local coding-agent HTTP server built on the official claude-agent-sdk.

Wraps a single persistent ClaudeSDKClient (which itself drives the Claude Code
CLI — file edits, bash, search, etc.) behind a tiny FastAPI server so other
local tools/scripts can talk to it over HTTP.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)

WORKSPACE = os.environ.get("WORKSPACE_ROOT", os.getcwd())
MODEL = os.environ.get("CLAUDE_MODEL", "claude-opus-4-8")

OPTIONS = ClaudeAgentOptions(
    cwd=WORKSPACE,
    model=MODEL,
    system_prompt=(
        "You are a local coding assistant running on the user's own machine. "
        "You have file and shell access scoped to the configured workspace "
        "directory. Make the requested changes directly rather than just "
        "describing them."
    ),
    # 'acceptEdits' lets file edits happen without a per-edit confirmation
    # prompt (there's no human in the loop on the other end of this HTTP API).
    # Bash commands still follow the SDK's default permission behavior.
    permission_mode="acceptEdits",
)

client: ClaudeSDKClient | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global client
    client = ClaudeSDKClient(options=OPTIONS)
    await client.connect()
    try:
        yield
    finally:
        await client.disconnect()


app = FastAPI(title="local-coding-agent", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    assert client is not None
    await client.query(req.message)

    parts: list[str] = []
    async for msg in client.receive_response():
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)

    return ChatResponse(response="".join(parts))


@app.post("/reset")
async def reset() -> dict:
    global client
    assert client is not None
    await client.disconnect()
    client = ClaudeSDKClient(options=OPTIONS)
    await client.connect()
    return {"ok": True}


@app.post("/interrupt")
async def interrupt() -> dict:
    assert client is not None
    await client.interrupt()
    return {"ok": True}


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "model": MODEL, "workspace": WORKSPACE}
