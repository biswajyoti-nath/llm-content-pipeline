# Hallucination Control Rules for LLM Prompts

A reference guide for writing prompts that minimize hallucination in content generation workflows.

---

## Core Rules (include in every prompt)

1. **Explicit source constraint**
   > "Use ONLY information explicitly present in the input text."

2. **Missing info handling**
   > "If information is missing, write 'Not mentioned' — do NOT infer or guess."

3. **No invention rule**
   > "Do NOT invent names, dates, numbers, or facts not present in the source."

4. **Output format lock**
   > "Output ONLY valid JSON." or "Follow the exact output structure below."

---

## Structural Techniques

### Separate extraction from generation
Instead of asking the model to extract AND write in one step, split it:
- Step 1: Extract key facts silently
- Step 2: Write using only those extracted facts

This forces the model to ground its output in source material before generating prose.

### Use null over guessing
For structured outputs, always instruct:
> "If a field is missing, return null. Do not guess or infer values."

### Ban specific clichés
Explicitly list phrases the model should never use:
> "Do NOT use: 'disrupting the industry', 'passionate founder', 'game-changing', 'revolutionary', 'innovative solution'."

---

## Model-Specific Notes

| Model | Hallucination Tendency | Mitigation |
|---|---|---|
| Claude | Low — prefers caution | Add explicit extraction step |
| Gemini | Medium — fills gaps confidently | Enforce null for missing fields |
| ChatGPT | Medium — creative by default | Strict role + format constraints |

---

## Red Flags in Output (review checklist)

- [ ] Specific numbers not in the source (revenue, users, funding)
- [ ] Dates that weren't mentioned
- [ ] Quotes that sound too polished
- [ ] Company details that feel assumed
- [ ] Generic motivational language

If any of these appear — the prompt needs stronger constraints.
