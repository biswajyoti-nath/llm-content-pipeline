"""
AI Content Pipeline — Full Multi-Model Version
-----------------------------------------------
A 3-stage pipeline for automated startup story generation.

Stage 1 — Discovery:    Tavily API searches for startup information
Stage 2 — Structuring:  Gemini extracts and structures the raw research
Stage 3 — Drafting:     Claude generates a publication-ready startup story

Usage:
    python pipeline.py --query "Zepto grocery delivery India"
    python pipeline.py --query "Zepto grocery delivery India" --save
    python pipeline.py --transcript examples/sample_transcript.txt --save

Requirements:
    pip install anthropic google-genai tavily-python python-dotenv

.env file:
    ANTHROPIC_API_KEY=your_key_here
    GEMINI_API_KEY=your_key_here
    TAVILY_API_KEY=your_key_here
"""

import anthropic
import argparse
import json
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient

load_dotenv()


# ── Prompts ────────────────────────────────────────────────────────────────────

GEMINI_STRUCTURING_PROMPT = """You are a structured data extraction system for a startup research pipeline.

You will receive raw search results about a startup or founder.
Extract and structure the information into clean JSON.

Rules:
1. Use ONLY information explicitly present in the search results.
2. If a field is missing or unclear, return null.
3. Do NOT guess or infer values.
4. Output ONLY valid JSON — no explanation, no markdown code blocks.

Schema:
{
  "founder_name": "string or null",
  "startup_name": "string or null",
  "industry": "string or null",
  "founding_year": "string or null",
  "location": "string or null",
  "problem_statement": "string or null",
  "solution": "string or null",
  "revenue": "string or null",
  "funding": "string or null",
  "traction": "string or null",
  "key_facts": ["list of verified facts from search results"]
}

Raw search results:
{search_results}
"""

CLAUDE_STORY_SYSTEM = """You are a startup journalist writing for a professional startup media platform.
Your writing is factual, specific, and free of generic motivational language.
Never use: 'disrupting the industry', 'passionate founder', 'game-changing', 'revolutionary', 'innovative solution'."""

CLAUDE_STORY_PROMPT = """Convert the structured startup brief below into a clean, publication-ready startup story.

Rules:
1. Do NOT invent or hallucinate any facts.
2. Use ONLY information present in the brief.
3. If information is missing, write "Not mentioned".
4. Professional journalistic tone — no cliches.

Before writing, silently extract:
- Founder name and background
- Core problem and solution
- Startup journey and timeline
- Key facts and traction signals

Output Structure:
## Headline
## Founder Background
## Startup Journey
## Problem & Solution
## Key Insights
## Startup Snapshot
(Format: Founder Name | Startup Name | Year | Industry)

Structured Brief:
{brief}
"""

CLAUDE_TRANSCRIPT_SYSTEM = """You are a startup journalist writing for a professional startup media platform.
Your writing is factual, specific, and free of generic motivational language.
Never use: 'disrupting the industry', 'passionate founder', 'game-changing', 'revolutionary'."""

CLAUDE_TRANSCRIPT_PROMPT = """Convert the raw founder interview transcript into a clean, structured startup story.

Rules:
1. Do NOT invent or hallucinate any facts.
2. Use ONLY information explicitly present in the transcript.
3. If information is missing, write "Not mentioned".
4. Ignore filler words, interruptions, and off-topic conversation.

Before writing, silently extract:
- Founder name and background
- Problem they faced
- How the idea started
- When the company was founded
- What the product does
- Key lessons or insights shared

Output Structure:
## Headline
## Founder Background
## Startup Journey
## Problem & Solution
## Key Insights
## Startup Snapshot
(Format: Founder Name | Startup Name | Year | Industry)

Transcript:
{transcript}
"""


# ── Stage 1: Discovery ─────────────────────────────────────────────────────────

def discover(query: str) -> str:
    """Stage 1: Search for startup information using Tavily."""
    print(f"\n[Stage 1 — Discovery] Searching: '{query}'...")

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=True
    )

    parts = []
    if response.get("answer"):
        parts.append(f"Summary: {response['answer']}\n")

    for i, result in enumerate(response.get("results", []), 1):
        parts.append(
            f"Source {i}: {result.get('title', '')}\n"
            f"URL: {result.get('url', '')}\n"
            f"Content: {result.get('content', '')}\n"
        )

    raw_research = "\n---\n".join(parts)
    print(f"[Stage 1] Done. Found {len(response.get('results', []))} sources.\n")
    return raw_research


# ── Stage 2: Structuring ───────────────────────────────────────────────────────

def structure(raw_research: str) -> dict:
    """Stage 2: Extract structured data from raw research using Gemini."""
    print("[Stage 2 — Structuring] Extracting structured data with Gemini...")

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    prompt = GEMINI_STRUCTURING_PROMPT.replace("{search_results}", raw_research)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt]
    )

    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("Warning: Gemini returned invalid JSON. Raw output:")
        print(raw)
        data = {}

    print("[Stage 2] Done.\n")
    return data


# ── Stage 3: Drafting ──────────────────────────────────────────────────────────

def draft_from_brief(brief: dict) -> str:
    """Stage 3a: Generate story from structured brief using Claude."""
    print("[Stage 3 — Drafting] Generating story with Claude...")

    client = anthropic.Anthropic()
    brief_text = json.dumps(brief, indent=2)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=CLAUDE_STORY_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": CLAUDE_STORY_PROMPT.replace("{brief}", brief_text)
            }
        ]
    )

    story = message.content[0].text
    print("[Stage 3] Done.\n")
    return story


def draft_from_transcript(transcript: str) -> str:
    """Stage 3b: Generate story directly from transcript using Claude."""
    print("[Stage 3 — Drafting] Generating story from transcript with Claude...")

    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=CLAUDE_TRANSCRIPT_SYSTEM,
        messages=[
            {
                "role": "user",
                "content": CLAUDE_TRANSCRIPT_PROMPT.replace("{transcript}", transcript)
            }
        ]
    )

    story = message.content[0].text
    print("[Stage 3] Done.\n")
    return story


# ── Output ─────────────────────────────────────────────────────────────────────

def save_output(story: str, brief: dict = None, output_dir: str = "output"):
    """Save story and structured brief to output files."""
    Path(output_dir).mkdir(exist_ok=True)

    story_path = Path(output_dir) / "story.md"
    story_path.write_text(story, encoding="utf-8")
    print(f"Story saved to: {story_path}")

    if brief:
        json_path = Path(output_dir) / "structured_brief.json"
        json_path.write_text(json.dumps(brief, indent=2), encoding="utf-8")
        print(f"Structured brief saved to: {json_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AI Content Pipeline — Multi-model startup story generator"
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--query", help="Search query for startup discovery (full pipeline)")
    input_group.add_argument("--transcript", help="Path to transcript .txt file (Stage 3 only)")

    parser.add_argument("--save", action="store_true", help="Save outputs to /output folder")
    args = parser.parse_args()

    brief = {}

    if args.query:
        print("=" * 60)
        print("Running full 3-stage pipeline")
        print("=" * 60)

        raw_research = discover(args.query)
        brief = structure(raw_research)

        print("Structured Brief:")
        print(json.dumps(brief, indent=2))
        print()

        story = draft_from_brief(brief)

    elif args.transcript:
        print("=" * 60)
        print("Running transcript-only mode (Stage 3)")
        print("=" * 60)

        path = Path(args.transcript)
        if not path.exists():
            print(f"Error: File not found — {args.transcript}")
            sys.exit(1)

        transcript = path.read_text(encoding="utf-8")
        print(f"Loaded transcript: {args.transcript} ({len(transcript)} chars)\n")
        story = draft_from_transcript(transcript)

    print("=" * 60)
    print(story)
    print("=" * 60)

    if args.save:
        save_output(story, brief if args.query else None)


if __name__ == "__main__":
    main()