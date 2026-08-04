"""OpenAI-backed natural-language chat and NL-to-SQL over a dataset's profile.

We never send the full raw dataset to the model. Instead we send the cached
profile (dtypes, stats, correlations, small preview) as grounding context,
which keeps prompts small and avoids leaking full customer data unnecessarily.
"""
from __future__ import annotations

import json
import re

from openai import OpenAI

from app.config import get_settings

settings = get_settings()
_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


SYSTEM_PROMPT = """You are InsightAI, a senior data analyst. You answer questions about a
tabular dataset using only the profile/statistics provided to you as context. Be concise,
concrete, and cite actual numbers from the context. If the context doesn't contain enough
information to answer confidently, say so plainly rather than guessing.

Respond ONLY as JSON with this exact shape:
{"text": "<answer in plain English>", "confidence": <0-100 integer>,
 "stats": {"<label>": "<value>"}, "chart_suggestion": "<bar|line|pie|scatter|none>"}
"""


def chat_about_dataset(profile: dict, question: str, history: list[dict]) -> dict:
    context = {
        "row_count": profile.get("row_count"),
        "columns": profile.get("columns"),
        "correlations": profile.get("correlations"),
        "duplicate_pct": profile.get("duplicate_pct"),
    }
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": f"Dataset profile:\n{json.dumps(context, default=str)[:12000]}"},
    ]
    for m in history[-6:]:
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": question})

    client = get_client()
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=messages,
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"text": raw, "confidence": 50, "stats": None, "chart_suggestion": "none"}


NL2SQL_SYSTEM = """You translate a plain-English question into a single read-only SQL
SELECT query against a table named `dataset` with the given columns and types. Only ever
output SQL — no prose, no markdown fences. Never use INSERT, UPDATE, DELETE, DROP, ALTER,
or multiple statements. If the question can't be expressed as a SELECT, output:
SELECT 'unsupported' AS error;
"""

_FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|alter|truncate|--|;.*\S)\b", re.IGNORECASE)


def nl_to_sql(columns: list[dict], question: str) -> str:
    col_desc = ", ".join(f"{c['name']} ({c['dtype']})" for c in columns)
    client = get_client()
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": NL2SQL_SYSTEM},
            {"role": "user", "content": f"Columns: {col_desc}\nQuestion: {question}"},
        ],
        temperature=0,
    )
    sql = response.choices[0].message.content.strip().strip("`")

    # Defense in depth: even though the prompt restricts to SELECT, validate before execution.
    if not sql.lower().startswith("select") or _FORBIDDEN.search(sql):
        raise ValueError("Generated query failed safety validation")
    return sql
