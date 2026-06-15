"""
AI client — wraps the Anthropic messages API with tool definitions
so the LLM can call search_opportunities and web_search.
"""
from __future__ import annotations

import os
import json
import re
from typing import Any

import anthropic

from utils.database import search_opportunities, format_for_chat


# ── Tool definitions ────────────────────────────────────────────────────────

TOOLS: list[dict] = [
    {
        "name": "search_opportunities",
        "description": (
            "Search the curated career database for jobs, internships, and scholarships. "
            "Use this first before web_search for any career-related request."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Keywords describing what the user wants"},
                "opp_type": {
                    "type": "string",
                    "enum": ["job", "internship", "scholarship", "any"],
                    "description": "Filter by opportunity type",
                },
                "field": {"type": "string", "description": "User's field of study or work (e.g. 'computer science')"},
                "education_level": {
                    "type": "string",
                    "description": "User's education level (e.g. 'bachelor', 'master', 'phd')",
                },
                "location": {"type": "string", "description": "Preferred location (city, state, or 'remote')"},
                "limit": {"type": "integer", "description": "Max results to return (default 5)"},
            },
            "required": [],
        },
    },
    {
        "name": "web_search",
        "description": (
            "Search the web for current information about specific companies, programs, or opportunities "
            "not found in the local database. Use sparingly and only after the database search."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Web search query string"},
            },
            "required": ["query"],
        },
    },
]


SYSTEM_PROMPT = """You are an AI career assistant for CareerPath AI. Your job is to help users discover jobs, internships, and scholarships that match their background, then guide them from search → application → interview.

## What You Do
1. Find opportunities matching field, education level, location, and career goals
2. Explain details clearly — eligibility, deadlines, and step-by-step application process in plain language  
3. Review application materials — resumes, cover letters, personal statements when shared
4. Prep for interviews — likely questions, answer frameworks, practice + feedback
5. Give honest career guidance — skill gaps to fix, alternative paths, realistic timelines

## How You Search
1. search_opportunities - Use this first for any job/internship/scholarship request. Searches curated, updated internal database.
2. web_search - Use only when database has few/no matches, user asks about specific company/university, or current info is needed.

## How You Respond
- Tone: Direct, warm, mentor-like. No filler.
- Personalize using user's field, location, experience, goals
- Listings format: **Title** — Organization — Location — Deadline — 1-line summary — link
- Advice format: 2-4 concrete next steps

## Rules
1. Never invent listings, deadlines, or links.
2. If nothing matches, say so + suggest how to broaden search.
3. For visa/immigration: general info only + official sources.
4. Don't ask for sensitive personal data unless required.
5. If request is vague, ask ONE focused clarifying question before searching."""


def _handle_tool_call(tool_name: str, tool_input: dict) -> str:
    """Execute a tool call and return a string result."""
    if tool_name == "search_opportunities":
        opp_type = tool_input.get("opp_type")
        if opp_type == "any":
            opp_type = None
        results = search_opportunities(
            query=tool_input.get("query", ""),
            opp_type=opp_type,
            field=tool_input.get("field"),
            education_level=tool_input.get("education_level"),
            location=tool_input.get("location"),
            limit=tool_input.get("limit", 6),
        )
        if not results:
            return "No matching opportunities found in the database for those criteria."
        return format_for_chat(results)

    if tool_name == "web_search":
        # In a deployed app this would call a real search API.
        # We return a helpful fallback so the LLM can still respond gracefully.
        return (
            f"Web search is not available in this environment. "
            f"Please advise the user to search directly for '{tool_input.get('query', '')}' "
            f"on Google, LinkedIn, or the organization's careers page."
        )

    return f"Unknown tool: {tool_name}"


def build_user_context(profile: dict) -> str:
    """Convert sidebar profile into a brief context string prepended to the first message."""
    parts = []
    if profile.get("field"):
        parts.append(f"Field: {profile['field']}")
    if profile.get("education"):
        parts.append(f"Education: {profile['education']}")
    if profile.get("location"):
        parts.append(f"Location: {profile['location']}")
    if profile.get("goals"):
        parts.append(f"Goals: {profile['goals']}")
    if not parts:
        return ""
    return "[User profile: " + " | ".join(parts) + "]"


def stream_response(
    messages: list[dict],
    profile: dict,
    file_text: str = "",
) -> str:
    """
    Send messages to Claude with tool support.
    Returns the final assistant text response.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))

    # Inject profile context into the first user message if present
    context = build_user_context(profile)
    api_messages = []
    for i, msg in enumerate(messages):
        if i == 0 and msg["role"] == "user" and context:
            content = f"{context}\n\n{msg['content']}"
            api_messages.append({"role": "user", "content": content})
        else:
            api_messages.append(msg)

    # Append uploaded file text if any
    if file_text and api_messages:
        last = api_messages[-1]
        if last["role"] == "user":
            last["content"] = last["content"] + f"\n\n[Uploaded document content]:\n{file_text}"

    # Agentic loop: handle tool calls until we get a final text response
    for _ in range(6):  # max 6 tool rounds
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=api_messages,
        )

        # Collect text and tool_use blocks
        text_parts: list[str] = []
        tool_uses: list[Any] = []

        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_uses.append(block)

        # If no tool calls, we're done
        if not tool_uses:
            return "\n".join(text_parts).strip()

        # Build assistant turn with mixed content
        assistant_content = []
        for block in response.content:
            if block.type == "text":
                assistant_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                assistant_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        api_messages.append({"role": "assistant", "content": assistant_content})

        # Execute tools and build tool_result turn
        tool_results = []
        for tu in tool_uses:
            result = _handle_tool_call(tu.name, tu.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.id,
                "content": result,
            })

        api_messages.append({"role": "user", "content": tool_results})

    return "I ran into an issue generating a response. Please try rephrasing your question."
