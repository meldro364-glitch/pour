---
name: pour
description: When the user asks for naming, open-ended brainstorming, reframing a stuck problem, devil's-advocate / pre-mortem, or a creative opening line, call mcp__pour__pour 1-2 times BEFORE composing the response to inject a random fragment from outside the LLM's training-distribution defaults. Use to break convergent thinking. Skip for factual Q&A, debugging, code completion, math, translation, or any task where the right answer is determinate.
version: 0.1.0
---

# pour

Outside-context injection for creative tasks. Conceptual descendant of Brian Eno's *Oblique Strategies*. Backed by an MCP tool `mcp__pour__pour` that returns one random fragment from curated public-knowledge sources (Wikiquote, Wikipedia, Public Domain Review, arXiv).

## When to use

Tasks where LLM outputs are known to converge on predictable patterns:

- **Naming** — products, features, projects, characters. Default LLM output cycles through "Synapse / Nexus / Pulse / Echo / Drift". A pour can drop in an unrelated domain (e.g., medieval bestiaries, 19th-century ballooning) that reframes the naming space.
- **Open-ended brainstorming** — "5 unusual ways to X". Without pour, the LLM produces tactics from the same well-trodden corner. With pour, you sometimes get a positional reframe.
- **Pre-mortem / devil's advocate** — "ways this could fail". LLMs are too polite by default. A pour can surface a *structural* failure mode that wouldn't otherwise.
- **Reframing a stuck problem** — "I'm stuck on X, what am I missing?". The whole value here is angle-of-view.
- **Creative openings** — essay hooks, talk intros, post leads. LLM defaults are tired.

## When NOT to use

- Factual Q&A where the right answer is determinate
- Code debugging or completion
- Mathematics / algorithm design
- Translation
- Step-by-step procedural tasks
- Any task where the user wants a specific answer, not exploration

Using pour in these contexts adds noise that the LLM then has to filter out, hurting output quality.

## How to use

1. **Call once** (`mcp__pour__pour` with no args, or `source="pdr"` / `"wq"` / `"wp"` / `"arxiv"` to force) before composing the response.
2. **Read the fragment**. Ask: does any concept, metaphor, era, or domain inside this fragment open a non-obvious angle on the user's task?
3. **If yes**: let it shape your response. Don't quote the fragment verbatim — let it inform the *frame* you bring.
4. **If no after 1 call**: call again (max 2-3 total per task). If still nothing useful, just answer normally. Don't force a connection that isn't there.

The fragment is a nudge, not an answer. The value is in the *shift of abstraction layer* it sometimes triggers, not in the fragment's literal content.

## Transparency

If the response was meaningfully shaped by a pour fragment, mention it briefly to the user — "thinking about your X, a fragment about Y came up which suggested Z". This builds calibration: the user learns when pour helps and when it doesn't, and the practice gets self-correcting over time.

## Honest caveats

- pour is an experimental tool, not a proven one. Treat each use as a data point.
- A single pour call should not delay a response by more than ~2 seconds.
- Source weights default to `pdr:4, wq:4, wp:3, arxiv:2`. PDR (Public Domain Review essay hooks) tends to give the highest signal per call.

## Where it lives

- MCP tool: `mcp__pour__pour` (already registered)
- Implementation: `~/projects/khalid/projects/pour/` (`pour.py` CLI + `pour_mcp.py` server)
