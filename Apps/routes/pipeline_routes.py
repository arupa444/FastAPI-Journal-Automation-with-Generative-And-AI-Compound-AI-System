from Apps.library_import import APIRouter, HTTPException
from Apps.models_journal import PulsusInputStr
from Apps.services.pipeline_service import PipelineService

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


@router.post("/journal-full-process")
async def journal_full_process(journal: PulsusInputStr):
    """
    Route that triggers the full journal -> PDF pipeline.
    """
    return await PipelineService.process_journal(journal)