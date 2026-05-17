# pour

A small tool that returns one random fragment from curated public knowledge sources, designed to be called by an LLM agent as a tool. The intent: inject outside-context content into reasoning to break out of convergent thinking patterns.

Conceptual descendant of Brian Eno's *Oblique Strategies* cards (1975) — but instead of a fixed deck, fetches live fragments from Wikiquote, Wikipedia, the Public Domain Review, and arXiv.

```
$ python3 pour.py --source pdr

[pdr] Vertiginous Accounts: Travels in the Air (1871 edition)
  https://publicdomainreview.org/collection/travels-in-the-air

Expedition accounts of aeronauts bravely venturing into the heavens on hot-air balloons.
```

## What's in this repo

| file | purpose |
|------|---------|
| `pour.py` | CLI + library. Implements the four sources. Zero dependencies beyond stdlib. |
| `pour_mcp.py` | MCP server wrapper. Exposes one tool, `pour`. |
| `SKILL.md` | Claude Code skill definition. Instructs Claude when to reach for the tool. |

## Install

### As a Python CLI

```bash
git clone https://github.com/meldro364-glitch/pour
cd pour
python3 pour.py            # one weighted-random fragment
python3 pour.py --source wq # force Wikiquote
python3 pour.py --n 5      # five fragments
python3 pour.py --json     # machine-readable
```

### As a Claude Code skill + MCP server

1. **Copy the skill** so Claude auto-triggers it for the right tasks:
   ```bash
   mkdir -p ~/.claude/skills/pour
   cp SKILL.md ~/.claude/skills/pour/SKILL.md
   ```
2. **Register the MCP server** so Claude can actually call `pour`:
   ```bash
   pip install mcp
   claude mcp add pour python3 -- "$(pwd)/pour_mcp.py"
   ```
3. Restart your Claude session. Verify with `claude mcp list` — `pour` should be ✓ Connected.

After this, when you give Claude a task that matches the skill's trigger (naming, open brainstorming, reframing, pre-mortem, creative openings), it will silently call `pour` 1–2 times before responding and let the fragment shape its frame.

## Sources

| flag | source | flavor |
|------|--------|--------|
| `pdr` | Public Domain Review RSS (essay hooks) | curated, surprising, paragraph-form |
| `wq` | Wikiquote random page → one quote | curated, quotable |
| `wp` | Wikipedia random article (REST summary) | broad, encyclopedic |
| `arxiv` | arXiv random abstract | academic, dense |

Default weights when no source is forced: `pdr:4, wq:4, wp:3, arxiv:2`. PDR tends to give the highest signal per call because every feed item is a hand-written editor's hook.

## When pour is useful

- **Naming** (products, features, projects) — LLM defaults cycle through "Synapse / Nexus / Pulse". A fragment from a 17th-century almanac can shift the whole naming space.
- **Open-ended brainstorming** — when the answer set is huge and the LLM keeps returning the same five tactical moves.
- **Pre-mortem / devil's advocate** — LLMs are too polite; a random failure-tale from history can surface a sharper critique.
- **Reframing a stuck problem** — when you suspect you're solving the wrong puzzle.
- **Creative openings** — essay hooks, talk intros, post leads.

## When pour is **not** useful

- Factual Q&A
- Code debugging or completion
- Mathematics or algorithm design
- Translation
- Step-by-step procedural tasks

In these contexts the random fragment is noise the model has to filter out, and it usually hurts. The skill description explicitly excludes these.

## Why it exists

LLMs converge on safe patterns. Even with temperature, the underlying distribution is what the model already learned — so the same metaphors, the same structural moves, the same vocabulary keep surfacing. Injecting *external* content from a curated source adds genuine surprise from outside the gradient.

This idea has thought-experiment precedent (Brian Eno's *Oblique Strategies* in 1975; Meghan McGrath's *Stuff Claude Says* essay asking what such a deck would look for an AI) but no deployed agentic implementation that I could find. `pour` is the first cut.

## Honest caveats

- The tool is experimental. Whether it actually helps versus a base LLM is an open question. Treat each use as a data point.
- Single-call evaluation is noisy. The value (if any) accumulates across many uses as the model starts noticing cross-domain hooks more often.
- Corpus quality is the whole game. The four sources here are decent but not optimal; adding hand-curated sources (Project Gutenberg slugs, Standard Ebooks excerpts, Oblique Strategies itself) is a natural next step.

## License

MIT. See [LICENSE](LICENSE).
