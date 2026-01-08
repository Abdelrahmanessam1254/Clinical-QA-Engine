# Clinical QA Engine

A backend API that analyzes clinical notes and returns quality scores + actionable feedback.

## What This Does

Takes a clinical note as input, sends it to an LLM with carefully structured prompts, and returns:

- A score (0-100)
- A letter grade (A+ to D)
- 3-5 specific issues with severity levels and suggested fixes

## How to Run It

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up your OpenAI key or Google or Grok

create a `.env` file:

put this in

```
# LLM Provider Configuration

LLM_PROVIDER=google
# LLM_PROVIDER=grok
# LLM_PROVIDER=openai

# API Keys (use the one that matches your LLM_PROVIDER)

GOOGLE_API_KEY=AIzaSyBhMP9xC3FB28qs52JvJL90uEzbqGwsKxQ
# XAI_API_KEY=your-grok-key-here
# OPENAI_API_KEY=sk-your-openai-key-here

# Model Selection

# google models
MODEL_NAME=gemini-2.5-flash
# MODEL_NAME=gemini-2.5-pro

# openai models
# MODEL_NAME=gpt-4o
# MODEL_NAME=gpt-4-turbo

# grok models
# MODEL_NAME=grok-beta
# MODEL_NAME=gpt-4o-mini
```

### 3. Start the server

```bash
python main.py
```

The API runs at `http://localhost:8000`

### 4. Test it

```bash
curl -X POST "http://localhost:8000/analyze-note" \
  -H "Content-Type: application/json" \
  -d '{
    "note_text": "Patient reports neck pain since MVA. Pain is 8/10. Prescribed ibuprofen.",
    "note_type": "Progress Note",
    "date_of_service": "2024-01-15",
    "date_of_injury": "2024-01-10"
  }'
```

Or open `http://localhost:8000/docs` for interactive API testing.

## there is also a root api ("/") for info on the current running service provider

## status : Working or not

## service : name of project

## provider : name of LLM Provider

## model : name of model based on provider

## How It Works

### The Flow

1. **Input validation** - FastAPI checks the request structure
2. **Prompt building** - I construct a detailed prompt with the QA rules in it
3. **LLM call** - Send to Google or Grok or OpenAI with JSON mode enabled
4. **Grade calculation** - Convert the score to a letter grade
5. **Response** - Return structured JSON

### The Prompt Strategy

This was the hardest part. I needed to:

- Get consistent JSON output (solved with `response_format`)
- Enforce the "no inventing facts" rule (instructions + examples)
- Control severity levels (clear definitions)
- Keep edits minimal ("1-2 sentences only")

I put the rules directly in the prompt instead of hoping the LLM would remember general instructions.

### Model Choice

Using `gemini-2.5-flash` beacuse it's free during development.

For production I'd use `gpt-4o` or `gpt-4-turbo` for better accuracy.
The code makes it easy to swap just change one line.

## Design Decisions & Tradeoffs

### What I Did

- **Simple architecture** - One file, one endpoint. Easy to understand and modify.
- **Prompt engineering over fine-tuning** - Faster to iterate, no training data needed
- **JSON mode** - Forces valid JSON from the LLM (no parsing nightmares)
- **0 temperature** - Known results (either know or don't know the answer) (to make it don't guess)
  (0. instead of default 0.7)
- **Clear error handling** - Returns errors when stuff breaks

### Tradeoffs I Made

1. **Using an LLM instead of rules engine**

   - Pros: Flexible, handles nuance, easier to expand
   - Cons: Costs money per call, slower, less predictable
   - Why: The spec needs understanding of clinical language, not just pattern matching

2. **Single file instead of modular structure**

   - Pros: Everything's right here, no jumping between files
   - Cons: Would get messy if this grew
   - Why: It's a proof of concept with one endpoint

3. **Synchronous processing**

   - Pros: Simple to reason about
   - Cons: Request waits for LLM response (can be 2-5 seconds)
   - Why: No queue infrastructure for a demo, but I'd add async workers for production

4. **No caching**

   - Pros: Always fresh analysis
   - Cons: Analyzing the same note twice costs 2x
   - Why: Didn't want to assume notes are immutable, but would add Redis for prod

5. **Grade calculation in code, not LLM**
   - Pros: Deterministic, no variation
   - Cons: One more thing to maintain
   - Why: Scoring should be controlled, not vibes-based

## What I'd Add for Production

- **Async processing** - Queue system so requests don't block
- **Caching layer** - Redis to cache identical note analyses
- **Monitoring** - Log LLM performance, track score distributions
- **Retry logic** - LLM calls can fail, need exponential backoff
- **Rate limiting** - Prevent abuse and manage API costs
- **Prompt versioning** - Track which prompt generated which analysis
- **A/B testing framework** - Compare prompt variations
- **Structured logging** - For debugging and auditing

## Swapping the LLM

To use a different model, change this in `.env`:

```python
# LLM_PROVIDER:
# from LLM_PROVIDER=google to # LLM_PROVIDER=grok

# MODEL_NAME:
# from MODEL_NAME=gemini-2.5-flash to # MODEL_NAME=grok-beta
```

The prompt should work with any decent LLM. Might need to tune temperature or adjust instructions slightly.

## Why This Approach

I focused on **controlling the LLM output** rather than building complex infrastructure. The hard part isn't the API wrapper - it's getting consistent, rule-following responses from a probabilistic system.

The prompt is doing most of the work. I spent time making it specific:

- Clear severity definitions
- Explicit examples of what NOT to do
- Structured output format
- Hard rules repeated multiple times

This is fragile in some ways (prompts can drift, LLMs update) but it's fast to iterate and easy to fix when it breaks.

## Questions I'd Ask Before Production

1. What's the expected volume? (affects infrastructure choices)
2. Are notes standardized or wildly varied? (affects prompt complexity)
3. Do we need audit trails of what changed? (affects data model)
4. What's the error tolerance? (affects quality controls)
5. Do different note types need different rubrics? (affects prompt routing)

---

Built in a few hours. It's not perfect but it works and shows the approach.
