from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from datetime import date
import os
import json
import httpx
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Clinical QA Engine")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google")  # "openai", "grok", or "google" default to google
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash") # default to google

# google
if LLM_PROVIDER == "google":
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    google_model = genai.GenerativeModel(MODEL_NAME)
    client = None
    # grok
elif LLM_PROVIDER == "grok":
    client = OpenAI(
        api_key=os.getenv("XAI_API_KEY"),
        base_url="https://api.x.ai/v1",
        timeout=httpx.Timeout(3600.0)
    )
else:  # openai
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class NoteInput(BaseModel):
    note_text: str
    note_type: str
    date_of_service: str
    date_of_injury: str

class QAFlag(BaseModel):
    severity: Literal["critical", "major", "minor"]
    issue: str
    why_it_matters: str
    suggested_edit: str

class QAResponse(BaseModel):
    score: int
    grade: str
    flags: List[QAFlag]

def calculate_grade(score: int) -> str:
    if score >= 97: return "A+"
    elif score >= 93: return "A"
    elif score >= 90: return "A-"
    elif score >= 87: return "B+"
    elif score >= 83: return "B"
    elif score >= 80: return "B-"
    elif score >= 77: return "C+"
    elif score >= 73: return "C"
    elif score >= 70: return "C-"
    else: return "D"

# Role prompt for QA analysis
def build_qa_prompt(note_text: str, note_type: str, dos: str, doi: str) -> str:
    return f"""You are a clinical documentation QA reviewer. Analyze this note and return ONLY valid JSON.

CLINICAL NOTE:
{note_text}

METADATA:
- Note Type: {note_type}
- Date of Service: {dos}
- Date of Injury: {doi}

YOUR TASK:
Return a JSON object with:
1. "score": integer 0-100 (quality score)
2. "flags": array of 3-5 issues, each with:
   - "severity": "critical" | "major" | "minor"
   - "issue": what's wrong 
   - "why_it_matters": clinical/legal reason
   - "suggested_edit": 1-2 sentence fix (minimal change only)

RULES YOU MUST FOLLOW:
- Do NOT invent facts or add information not in the note
- Do NOT rewrite entire sections
- Flag missing information as "Information missing: [what]"
- Check if patient-reported history is separated from clinician findings
- Check for defensive, neutral language
- Flag unsupported claims or editorializing
- Check date consistency with DOS/DOI

SEVERITY LEVELS:
- critical: Missing required info, legal exposure, contradictions
- major: Unclear documentation, missing key details
- minor: Style issues, minor clarifications needed

Return ONLY the JSON, no explanation."""

# Google 
def call_google_ai(prompt: str) -> dict:
    response = google_model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            temperature=0,
            response_mime_type="application/json"
        )
    )
    return json.loads(response.text)

# OpenAI or Grok (OpenAI-compatible APIs)
def call_openai_compatible(prompt: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a clinical QA expert. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"} if LLM_PROVIDER == "openai" else None
    )
    return json.loads(response.choices[0].message.content)

# Main analysis endpoint
@app.post("/analyze-note", response_model=QAResponse)
async def analyze_note(input_data: NoteInput):
    if not input_data.note_text.strip():
        raise HTTPException(status_code=400, detail="Note text cannot be empty")

    try:
        # write the prompt
        prompt = build_qa_prompt(
            input_data.note_text,
            input_data.note_type,
            input_data.date_of_service,
            input_data.date_of_injury
        )

        # call the appropriate LLM

        if LLM_PROVIDER == "google":
            result = call_google_ai(prompt)
        else:
            result = call_openai_compatible(prompt)
        
        # parse the result

        score = result.get("score", 0)
        grade = calculate_grade(score)
        
        return QAResponse(
            score=score,
            grade=grade,
            flags=[QAFlag(**flag) for flag in result.get("flags", [])]
        )
        
        # handle JSON parsing errors
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="LLM returned invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok", 
        "service": "Clinical QA Engine",
        "provider": LLM_PROVIDER,
        "model": MODEL_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)