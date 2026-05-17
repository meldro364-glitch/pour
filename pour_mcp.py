"""
MCP server wrapping pour. Exposes one tool: `pour`, callable by an LLM agent
to fetch a random fragment from a curated public knowledge source.

Run with: python3 pour_mcp.py
Register with Claude Code:
    claude mcp add pour python3 -- /abs/path/to/pour_mcp.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make sibling pour.py importable when launched via absolute path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP  # noqa: E402

import pour as _pour  # noqa: E402

mcp = FastMCP("pour")


@mcp.tool(
    description=(
        "Return ONE random fragment from a curated public-knowledge source. "
        "Intended to inject outside-context content into your thinking when a task "
        "would benefit from a non-obvious angle (naming, brainstorming, reframing, "
        "creative openings, devil's-advocate prompts). The fragment is random — "
        "you do NOT pick its content, only optionally its source. Use sparingly; "
        "if the first fragment doesn't help, you may call again, but cap at ~3 "
        "tries per task to avoid spinning. Sources: 'wq' Wikiquote (curated quotes), "
        "'wp' Wikipedia (broad encyclopedic), 'arxiv' (academic abstracts). Omit "
        "source for a weighted random pick (wq:5 / wp:4 / arxiv:2)."
    )
)
def pour(source: str | None = None) -> dict:
    """Pour one random fragment.

    Args:
        source: Optional. One of 'wq', 'wp', 'arxiv'. Omit for weighted random.

    Returns:
        A dict with keys: source (str), title (str), url (str), text (str).
    """
    return _pour.pour(source)


if __name__ == "__main__":
    mcp.run()
