"""
pour — a tool that returns a random inspirational fragment from curated sources.

The intent: give an LLM (or a human) a small jolt of outside-context content to
break out of convergent thinking patterns. Conceptual descendant of Brian Eno's
Oblique Strategies cards (1975), but instead of fixed prompts, fetches live
fragments from public knowledge sources.

Usage (CLI):
    python3 pour.py               # one random fragment, any source
    python3 pour.py --source wq   # force a specific source
    python3 pour.py --n 5         # five fragments

Sources implemented in this first cut:
    wp      Wikipedia random article (REST summary). Broad, encyclopedic.
    wq      Wikiquote random page → parse one quote. Curated by humans as quotable.
    arxiv   Random arXiv abstract from a valid yymm.NNNNN range. Academic.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import unquote
from urllib.request import Request, urlopen

UA = "pour/0.1 (https://github.com/meldro364-glitch/khalid)"
TIMEOUT = 10


def _get(url: str, accept: str = "*/*") -> str:
    req = Request(url, headers={"User-Agent": UA, "Accept": accept})
    return urlopen(req, timeout=TIMEOUT).read().decode("utf-8", errors="replace")


def _get_with_final_url(url: str, accept: str = "*/*") -> tuple[str, str]:
    """Returns (final_url_after_redirects, body)."""
    req = Request(url, headers={"User-Agent": UA, "Accept": accept})
    resp = urlopen(req, timeout=TIMEOUT)
    return resp.geturl(), resp.read().decode("utf-8", errors="replace")


def _strip_html(s: str) -> str:
    """Crude HTML → text."""
    s = re.sub(r"<sup[^>]*>.*?</sup>", "", s, flags=re.DOTALL)  # drop footnote markers
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"&amp;", "&", s)
    s = re.sub(r"&quot;", '"', s)
    s = re.sub(r"&#39;", "'", s)
    s = re.sub(r"&lt;", "<", s)
    s = re.sub(r"&gt;", ">", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


# ---------- sources ----------

def pour_wikipedia() -> dict:
    """Random Wikipedia article via REST API."""
    url = "https://en.wikipedia.org/api/rest_v1/page/random/summary"
    body = _get(url, accept="application/json")
    data = json.loads(body)
    return {
        "source": "wikipedia",
        "title": data.get("title", "(untitled)"),
        "url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        "text": data.get("extract", "").strip(),
    }


_WQ_REJECT_PATTERNS = (
    re.compile(r"\bquotes? (about|at|by|on) ", re.IGNORECASE),
    re.compile(r"\b(at the )?Internet Movie Database\b", re.IGNORECASE),
    re.compile(r"\b(at|on) Wikiquote\b", re.IGNORECASE),
    re.compile(r"\bWikipedia article\b", re.IGNORECASE),
    re.compile(r"^(See also|External links?|References|Notes|Further reading|Bibliography)\b", re.IGNORECASE),
    re.compile(r"^[A-Z][a-z]+ (page|article|category)\b"),
)


def _is_quote_like(text: str) -> bool:
    if not (40 <= len(text) <= 400):
        return False
    if sum(c.isalpha() for c in text) < 30:
        return False
    if any(p.search(text) for p in _WQ_REJECT_PATTERNS):
        return False
    # Reject lines that look like a single linked title rather than a sentence.
    if text.count(" ") < 6:
        return False
    return True


def pour_wikiquote() -> dict:
    """Random Wikiquote page → extract one quote from the page body."""
    url = "https://en.wikiquote.org/wiki/Special:Random"
    final_url, html = _get_with_final_url(url, accept="text/html")
    title = unquote(final_url.split("/wiki/")[-1]).replace("_", " ")

    # Wikiquote pages list quotes as <li> items inside the parser output.
    parser_match = re.search(
        r'<div[^>]*class="mw-parser-output"[^>]*>(.*?)</div>\s*(?:<noscript>|<div class="printfooter")',
        html,
        re.DOTALL,
    )
    body_html = parser_match.group(1) if parser_match else html

    candidates = []
    for m in re.finditer(r"<li>(.*?)</li>", body_html, re.DOTALL):
        chunk = m.group(1)
        # Cut off at the first nested <ul> — that's usually source attribution.
        chunk_lead = re.split(r"<ul[\s>]", chunk, maxsplit=1)[0]
        text = _strip_html(chunk_lead)
        if _is_quote_like(text):
            candidates.append(text)
    text = random.choice(candidates) if candidates else "(no quote extractable)"
    return {
        "source": "wikiquote",
        "title": title,
        "url": final_url,
        "text": text,
    }


def pour_arxiv() -> dict:
    """Random arXiv abstract by picking a plausible ID in the recent past.

    arXiv IDs since 2007 use the format YYMM.NNNNN. Older IDs are
    archive-specific. We pick a yymm in the last ~5 years and a paper number,
    retrying on 404.
    """
    for _ in range(8):
        # year 2020..2025-ish
        y = random.randint(20, 25)
        mo = random.randint(1, 12)
        # Submission counts vary by month; 16000 is conservative
        n = random.randint(1, 15000)
        arxiv_id = f"{y:02d}{mo:02d}.{n:05d}"
        url = f"https://export.arxiv.org/abs/{arxiv_id}"
        try:
            html = _get(url, accept="text/html")
        except HTTPError as e:
            if e.code == 404:
                continue
            raise
        title_m = re.search(r'<meta name="citation_title" content="([^"]+)"', html)
        abs_m = re.search(r'<blockquote class="abstract[^"]*">(.*?)</blockquote>', html, re.DOTALL)
        if not abs_m:
            continue
        title = title_m.group(1).strip() if title_m else "(untitled)"
        text = _strip_html(abs_m.group(1))
        # Strip leading "Abstract:" label
        text = re.sub(r"^Abstract:\s*", "", text, flags=re.IGNORECASE)
        return {
            "source": "arxiv",
            "title": title,
            "url": url,
            "text": text,
        }
    return {"source": "arxiv", "title": "(no paper found)", "url": "", "text": ""}


def pour_pdr() -> dict:
    """Random Public Domain Review essay hook from their RSS feed.

    The feed's `<description>` for each item is a hand-written one-paragraph hook
    by the PDR editors. Highest-curation source in this kit.
    """
    import xml.etree.ElementTree as ET
    body = _get("https://publicdomainreview.org/rss.xml", accept="application/rss+xml")
    root = ET.fromstring(body)
    items = root.findall(".//item")
    if not items:
        return {"source": "pdr", "title": "(feed empty)", "url": "", "text": ""}
    item = random.choice(items)
    def _text(tag: str) -> str:
        el = item.find(tag)
        return (el.text or "").strip() if el is not None else ""
    title = _text("title")
    desc = _strip_html(_text("description"))
    link = _text("link")
    return {
        "source": "pdr",
        "title": title,
        "url": link,
        "text": desc,
    }


SOURCES = {
    "wp": pour_wikipedia,
    "wq": pour_wikiquote,
    "arxiv": pour_arxiv,
    "pdr": pour_pdr,
}


def pour(source: str | None = None) -> dict:
    """Return one random fragment. If source is None, pick weighted random.

    Default weights favor Wikiquote (most curated) and Wikipedia (broadest).
    """
    if source:
        fn = SOURCES.get(source)
        if not fn:
            raise ValueError(f"unknown source '{source}', try {list(SOURCES)}")
        return fn()
    pick = random.choices(["pdr", "wq", "wp", "arxiv"], weights=[4, 4, 3, 2], k=1)[0]
    return SOURCES[pick]()


# ---------- CLI ----------

def _format(item: dict) -> str:
    head = f"[{item['source']}] {item['title']}"
    if item.get("url"):
        head += f"\n  {item['url']}"
    return f"{head}\n\n{item['text']}\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="pour", description="Pour a random fragment.")
    p.add_argument("--source", choices=list(SOURCES), help="Force a specific source.")
    p.add_argument("--n", type=int, default=1, help="How many fragments to pour.")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = p.parse_args(argv)

    out = []
    for _ in range(args.n):
        try:
            out.append(pour(args.source))
        except (HTTPError, URLError) as e:
            sys.stderr.write(f"error: {e}\n")
            return 2

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        for item in out:
            print(_format(item))
            print("-" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
