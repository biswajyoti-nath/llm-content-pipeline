"""
AI Content Pipeline
-------------------
A multi-stage pipeline that converts raw founder interview transcripts
into structured startup stories and extracts JSON data for CMS storage.

Usage:
    python pipeline.py --transcript examples/sample_transcript.txt
    python pipeline.py --transcript examples/sample_transcript.txt --extract

Requirements:
    pip install anthropic
    Set your API key: export ANTHROPIC_API_KEY=your_key_here
"""

import anthropic
import argparse
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # Loads ANTHROPIC_API_KEY from .env file automatically


# ── Prompts ────────────────────────────────────────────────────────────────────

STORY_SYSTEM_PROMPT = """You are a startup journalist writing for a professional startup media platform.
Your writing is factual, specific, and free of generic motivational language.
You never use phrases like 'disrupting the industry', 'passionate founder', 'game-changing', or 'revolutionary'."""

STORY_USER_PROMPT = """Convert the raw founder interview transcript below into a clean, structured startup story.

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
{transcript}"""

EXTRACTION_SYSTEM_PROMPT = """You are a structured data extraction system.
You output only valid JSON. No explanation, no preamble, no markdown code blocks."""

EXTRACTION_USER_PROMPT = """Read the startup story below and extract the following fields into valid JSON.

Rules:
1. Use ONLY information explicitly present in the text.
2. If a field is missing, return null — do NOT guess or infer.
3. Output ONLY valid JSON.

Schema:
{{
  "founder_name": "string or null",
  "startup_name": "string or null",
  "industry": "string or null",
  "revenue": "string or null",
  "founding_year": "string or null",
  "location": "string or null"
}}

Story:
{story}"""


# ── Pipeline Functions ─────────────────────────────────────────────────────────

def load_transcript(filepath: str) -> str:
    """Load transcript from a text file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found — {filepath}")
        sys.exit(1)
    return path.read_text(encoding="utf-8")


def generate_story(client: anthropic.Anthropic, transcript: str) -> str:
    """Stage 1: Convert transcript to structured startup story using Claude."""
    print("\n[Stage 1] Generating story from transcript...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=STORY_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": STORY_USER_PROMPT.format(transcript=transcript)
            }
        ]
    )

    story = message.content[0].text
    print("[Stage 1] Done.\n")
    return story


def extract_data(client: anthropic.Anthropic, story: str) -> dict:
    """Stage 2: Extract structured JSON data from the generated story."""
    print("[Stage 2] Extracting structured data...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": EXTRACTION_USER_PROMPT.format(story=story)
            }
        ]
    )

    raw = message.content[0].text.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("Warning: Could not parse JSON response. Raw output:")
        print(raw)
        data = {}

    print("[Stage 2] Done.\n")
    return data


def save_output(story: str, data: dict, output_dir: str = "output"):
    """Save story and JSON to output files."""
    Path(output_dir).mkdir(exist_ok=True)

    story_path = Path(output_dir) / "story.md"
    story_path.write_text(story, encoding="utf-8")
    print(f"Story saved to: {story_path}")

    if data:
        json_path = Path(output_dir) / "extracted_data.json"
        json_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Extracted data saved to: {json_path}")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Content Pipeline — Transcript to Story")
    parser.add_argument("--transcript", required=True, help="Path to transcript .txt file")
    parser.add_argument("--extract", action="store_true", help="Also extract structured JSON data")
    parser.add_argument("--save", action="store_true", help="Save outputs to /output folder")
    args = parser.parse_args()

    # Init client (reads ANTHROPIC_API_KEY from environment)
    client = anthropic.Anthropic()

    # Load transcript
    transcript = load_transcript(args.transcript)
    print(f"Loaded transcript: {args.transcript} ({len(transcript)} chars)")

    # Stage 1: Generate story
    story = generate_story(client, transcript)
    print("=" * 60)
    print(story)
    print("=" * 60)

    # Stage 2: Extract data (optional)
    extracted = {}
    if args.extract:
        extracted = extract_data(client, story)
        print("Extracted Data:")
        print(json.dumps(extracted, indent=2))

    # Save outputs (optional)
    if args.save:
        save_output(story, extracted)


if __name__ == "__main__":
    main()