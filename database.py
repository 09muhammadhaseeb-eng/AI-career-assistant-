"""
Opportunity search utility — queries the local JSON database.
"""
from __future__ import annotations

import json
import os
from typing import Optional

import pandas as pd

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "opportunities.json")


def _load() -> list[dict]:
    with open(_DATA_PATH, "r") as f:
        return json.load(f)


def search_opportunities(
    query: str = "",
    opp_type: Optional[str] = None,          # "job" | "internship" | "scholarship"
    field: Optional[str] = None,
    education_level: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 6,
) -> list[dict]:
    """
    Search the curated opportunity database.

    Returns a ranked list of matching dicts (empty list if nothing matches).
    """
    records = _load()
    query_lower = query.lower()

    scored: list[tuple[int, dict]] = []

    for r in records:
        score = 0

        # ── Type filter (hard filter if specified) ──────────────────────
        if opp_type and r["type"] != opp_type.lower():
            continue

        # ── Education filter ────────────────────────────────────────────
        if education_level:
            edu_lower = education_level.lower()
            # Map common synonyms
            edu_map = {
                "undergrad": "bachelor",
                "undergraduate": "bachelor",
                "bs": "bachelor",
                "ba": "bachelor",
                "ms": "master",
                "masters": "master",
                "mba": "master",
                "doctorate": "phd",
                "doctoral": "phd",
            }
            edu_lower = edu_map.get(edu_lower, edu_lower)
            if edu_lower not in [e.lower() for e in r["education_level"]]:
                continue

        # ── Keyword matching (query, field, location) ───────────────────
        searchable = " ".join([
            r["title"],
            r["organization"],
            r["location"],
            r["summary"],
            " ".join(r["field"]),
            " ".join(r["tags"]),
        ]).lower()

        # Free-text query
        if query_lower:
            terms = query_lower.split()
            for term in terms:
                if term in searchable:
                    score += 3

        # Field match
        if field:
            field_lower = field.lower()
            for f in r["field"]:
                if field_lower in f.lower() or f.lower() in field_lower:
                    score += 5
            for tag in r["tags"]:
                if field_lower in tag.lower():
                    score += 2

        # Location match
        if location:
            loc_lower = location.lower()
            if loc_lower in r["location"].lower() or "remote" in r["location"].lower():
                score += 3
            if "united states" in r["location"].lower() and loc_lower in ["us", "usa", "united states", "america"]:
                score += 2

        # Always include everything if no filters given (score = 1 floor)
        if not query and not field and not location:
            score = max(score, 1)

        if score > 0:
            scored.append((score, r))

    # Sort descending by score
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:limit]]


def get_all_as_dataframe() -> pd.DataFrame:
    return pd.DataFrame(_load())


def format_for_chat(results: list[dict]) -> str:
    """Format results as Markdown for the chat window."""
    if not results:
        return ""
    lines = []
    for r in results:
        icon = {"job": "💼", "internship": "🎓", "scholarship": "🏆"}.get(r["type"], "📌")
        lines.append(
            f"{icon} **{r['title']}** — {r['organization']} — {r['location']} "
            f"— Deadline: {r['deadline']}\n"
            f"   {r['summary']}\n"
            f"   🔗 [Apply / Learn More]({r['link']})\n"
        )
    return "\n".join(lines)
