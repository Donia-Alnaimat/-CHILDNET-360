import os
from pathlib import Path
import requests as cn_requests
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel as CNBaseModel
from fastapi.middleware.cors import CORSMiddleware
from evaluation.demo_system import (
    ChildNetCoordinator,
    run_progressive_scenario,
)

class CNChatRequest(CNBaseModel):
    message: str
    top_k: int = 5
app = FastAPI(title="CHILDNET 360 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"]
)
from functools import lru_cache
@lru_cache(maxsize=1)
def get_coordinator():
    return ChildNetCoordinator()
    
@app.post("/agent-chat")
def childnet_agent_chat(request: CNChatRequest):

    question = request.message.strip()

    if not question:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty"
        )

    coordinator = get_coordinator()
    agent = coordinator.policy_agent

    comparison = agent.compare_jurisdictions(
        question,
        top_k=max(1, min(request.top_k, 10))
    )

    sources = (
        comparison.get("uae_federal_evidence", [])
        + comparison.get("dubai_evidence", [])
        + comparison.get("global_evidence", [])
    )

    if not sources:
        return {
            "answer": "No verified policy evidence retrieved.",
            "sources": [],
            "mode": "NO_EVIDENCE"
        }

    context = "\\n\\n".join(
        f"[{i}] {item['document']} | Page {item['page']} "
        f"| Jurisdiction: {item['jurisdiction']}\\n"
        f"{item['text'][:900]}"
        for i, item in enumerate(sources, 1)
    )

    prompt = (
        "You are CHILDNET 360, a policy evidence assistant. "
        "Answer using ONLY the supplied evidence. "
        "Cite source numbers such as [1] and [2]. "
        "Distinguish UAE law from international guidance. "
        "Do not invent legal obligations or citations. "
        "If evidence is insufficient, say so. "
        "Do not provide a definitive legal conclusion.\\n\\n"
        f"QUESTION: {question}\\n\\n"
        f"EVIDENCE:\\n{context}"
    )

    try:
        

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is missing")

        response = cn_requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent",
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json"
            },
            json={
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": prompt}]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 1200
                }
            },
            timeout=90
        )

        response.raise_for_status()
        result = response.json()


        answer = "".join(
            part.get("text", "")
            for candidate in result.get("candidates", [])
            for part in candidate.get("content", {}).get("parts", [])
        ).strip()

        if not answer:
            raise RuntimeError("Empty Gemini response")

        mode = "GEMINI_RAG"

    except Exception as exc:
        print("Gemini error:", str(exc))

        answer = (
            "The AI model is currently unavailable. "
            "Relevant policy evidence is provided below."
        )

        mode = "EVIDENCE_ONLY"


    return {
        "answer": answer,
        "sources": sources,
        "mode": mode,
        "legal_gap_confirmed": False,
        "requires_human_verification": True
    }

# CHILDNET 360 — SCENARIO & POLICY ENDPOINTS

@app.get("/progressive-scenario")
def progressive_scenario_api():
    coordinator = get_coordinator()
    return run_progressive_scenario(coordinator)

   


@app.get("/policy-intelligence")
def policy_intelligence_api(query: str, top_k: int = 3):
    coordinator = get_coordinator()

    result = coordinator.policy_agent.compare_jurisdictions(
        query,
        top_k=max(1, min(top_k, 5))
    )

    return {
        "query": query,
        "uae_federal": result.get("uae_federal_evidence", []),
        "dubai": result.get("dubai_evidence", []),
        "global": result.get("global_evidence", []),
        "human_verification_required": True,
        "legal_gap_confirmed": False
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "CHILDNET 360"
    }

class CNHelpRequest(CNBaseModel):
    request_id: str
    event_type: str
@app.post("/api/help")
def receive_help_request(request: CNHelpRequest):

    if request.event_type != "help_request":
        raise HTTPException(
            status_code=422,
            detail="Unsupported event type"
        )

    coordinator = ChildNetCoordinator()

    result = coordinator.process_event({
        "event_type": "help_request",
        "request_id": request.request_id,
        "description": "Simulated child help request"
    })

    return {
        "case_id": result["case_id"],
        "request_id": request.request_id,
        "decision": result["decision"],
        "demo_mode": True,
        "message": "Simulated request processed successfully."
    }

# ==========================================
# CHILDNET 360 — PUBLIC WEBSITE
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

WEB_DIRECTORY = PROJECT_ROOT / "web"

app.mount(
    "/web",
    StaticFiles(
        directory=str(WEB_DIRECTORY),
        html=True
    ),
    name="web"
)


@app.get("/", include_in_schema=False)
def childnet_home():
    return RedirectResponse(url="/web/")

    