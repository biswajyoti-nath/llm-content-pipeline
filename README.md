# AI Content Pipeline — Multi-Model LLM Workflow Design

A practical AI workflow that automates startup story production using three specialized LLMs in sequence — cutting manual research and drafting time from several hours to under 30 minutes.

---

## The Problem

Content teams producing startup stories manually spend hours on:
- Researching founders and funding activity across scattered sources
- Structuring unorganized research into clean briefs
- Drafting publication-ready articles from scratch

This pipeline automates all three stages using purpose-selected AI models.

---

## Workflow Architecture

```
Perplexity AI  →  Gemini  →  Claude
  Discovery       Structuring   Drafting
```

### Stage 1 — Discovery (Perplexity AI)
- Scans startup news, Product Hunt, funding announcements, LinkedIn
- Returns founder names, descriptions, funding info, and verified source links
- Output: 5–10 story candidates per day with cited references

### Stage 2 — Structuring (Gemini)
- Analyses unstructured research from Stage 1
- Extracts: founder background, founding year, problem statement, target market, traction signals
- Output: Clean JSON or markdown brief with all story elements

### Stage 3 — Drafting (Claude)
- Takes structured brief as input
- Generates full article: Headline / Founder Background / Startup Journey / Problem-Solution / Key Insights / Snapshot
- Output: Publication-ready draft requiring only minor editorial review

---

## Prompts

### Transcript-to-Story Prompt (Task 1)

```
Role: Startup journalist writing for a startup media platform.

Task: Convert the raw founder interview transcript into a clean, structured startup story.

Rules:
1. Do NOT invent or hallucinate any facts.
2. Use only information explicitly present in the transcript.
3. If information is missing, write "Not mentioned".
4. Maintain a professional journalistic tone.

Output Structure:
Headline | Founder Background | Startup Journey | Problem & Solution | Key Insights | Startup Snapshot
```

**Why this structure works:**
- Role prompting guides narrative tone toward media publication
- Hallucination control prevents invented facts
- Predefined sections ensure consistent, publishable output
- Missing info rule forces honesty over guesswork

---

### Data Extraction Prompt (Task 2)

```
You are a structured data extraction system.

Read the startup story below and extract the following fields:
- Founder Name
- Startup Name
- Industry
- Revenue (if mentioned)

Rules:
1. Use only information explicitly present in the text.
2. If a field is missing, return null.
3. Do not guess or infer values.
4. Output ONLY valid JSON.

Startup Story: [INSERT TEXT HERE]
```

**Output Schema:**
```json
{
  "founder_name": "string or null",
  "startup_name": "string or null",
  "industry": "string or null",
  "revenue": "string or null"
}
```

---

## Model Comparison — Claude vs Gemini

| Dimension | Claude | Gemini |
|---|---|---|
| Prompt engineering depth | Strong — internal reasoning, negative constraints | Simpler — fewer constraints |
| Task execution | Optimises for robustness | Executes end-to-end |
| Ecosystem grounding | Requires explicit instruction | Includes context naturally |
| Best suited for | Scalable workflow design | Practical content generation |

**Key insight:** Claude and Gemini have complementary strengths. Claude builds better prompt frameworks. Gemini executes more reliably out of the box. The best workflows use both strategically.

---

## Why AI Stories Sound Generic (And How to Fix It)

LLMs generate text based on statistical probability, not lived experience. Training on thousands of startup articles embeds repeated patterns — *"disrupting the industry"*, *"passionate founder"*.

**Prompt-level fixes:**
- Assign a precise role — not just "writer" but "startup journalist"
- Ban specific clichés explicitly in the prompt
- Separate extraction and writing into two steps
- Require concrete sections: problem trigger, early obstacle, traction signal

**System-level fixes:**
- **RAG:** Ground the model in real interview transcripts and founder data
- **Few-shot prompting:** Provide examples of high-quality stories
- **Human-in-the-loop:** AI drafts, editor refines tone and accuracy

---

## Tech Stack

- Perplexity AI — web-grounded research
- Google Gemini — structured extraction
- Anthropic Claude — narrative generation
- JSON — data schema for CMS integration

---

## Author

**Biswajyoti Nath**
B.Tech Computer Science, Barak Valley Engineering College
[LinkedIn](https://linkedin.com/in/biswajyoti-nath-984404323) | [Portfolio](https://biswajyoti-nath.github.io)
