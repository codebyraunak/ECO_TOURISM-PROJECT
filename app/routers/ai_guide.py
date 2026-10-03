from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlmodel import Session

from app.database import get_db
from app.dependencies import get_current_user_optional
from app.schemas import AIRequest, AIResponse
from app.services.ai_guide import generate_response

router = APIRouter(tags=["AI Guide"])


@router.get("/ai-guide")
def ai_guide_page(request: Request, db: Session = Depends(get_db)):
    """Render the interactive EcoGuide AI Travel Assistant interface."""
    user = get_current_user_optional(request, db)
    suggested_prompts = [
        "Plan a 3-day sustainable weekend trip to Coorg with eco-homestays",
        "What are the top hidden waterfalls in the Western Ghats of Karnataka?",
        "Best wildlife sanctuaries in Karnataka for a family safari?",
        "How can I practice Leave No Trace travel while trekking in Kudremukh?",
        "Recommend traditional Malnad and Coastal Karnataka vegetarian delicacies",
        "Best budget-friendly eco-destinations accessible by KSRTC bus from Bangalore"
    ]
    return request.app.state.templates.TemplateResponse(
        "ai_guide.html",
        {
            "request": request,
            "user": user,
            "suggested_prompts": suggested_prompts,
        },
    )


@router.post("/ai-guide/chat", response_model=AIResponse)
def ai_guide_chat(request: AIRequest):
    """API endpoint for AI-powered Karnataka travel guidance."""
    answer = generate_response(
        message=request.message,
        language=request.language or "English",
    )
    return {
        "answer": answer,
        "language": request.language or "English",
    }
