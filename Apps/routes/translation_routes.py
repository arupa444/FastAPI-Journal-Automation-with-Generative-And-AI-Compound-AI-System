from fastapi import APIRouter
from Apps.models_journal import TranslatePage
from Apps.services.translation_pipeline_service import TranslationPipelineService
from Apps.services.translate_service import TranslationService

router = APIRouter(prefix="/pdfs", tags=["Translation"])
# Initialize translation service
Translator = TranslationService()

@router.post("/translate")
async def translate_pdf(translatePage: TranslatePage):
    """
    Endpoint to translate an existing journal output into another language (PDF + HTML)
    """
    return await TranslationPipelineService.translate_journal(translatePage)
