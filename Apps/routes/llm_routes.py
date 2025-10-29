from fastapi import APIRouter
from Apps.models_journal import GeminiRequest, GroqRequest, CoreRequest
from Apps.services.llm_service import LLMService

router = APIRouter(prefix="/llm", tags=["LLM Operations"])


@router.post("/ask-gemini")
def pulsus_ask_gemini(req: GeminiRequest):
    """Handle Gemini prompt requests."""
    response = LLMService.process_gemini(req.prompt)
    return {"response": response}


@router.post("/ask-groq")
def pulsus_ask_groq(req: GroqRequest):
    """Handle Groq (LLaMA) prompt requests."""
    response = LLMService.process_groq(req.prompt)
    return {"response": response}


@router.post("/core/search")
async def search_articles(req: CoreRequest):
    """Search scholarly articles using the CORE API."""
    return await LLMService.process_core_search(req.prompt)