# app.py
from Apps.library_import import *
from Apps.config import Config
from Apps.services.translate_service import TranslationService
from Apps.routes.ui_routes import router as ui_router
from Apps.routes.journal_routes import router as journal_router
from Apps.routes.llm_routes import router as llm_router
from Apps.routes.pipeline_routes import router as pipeline_router
from Apps.routes.translation_routes import router as translation_router


# Initialize translation service
Translator = TranslationService()

# Initialize app & configuration
app = Config.create_app()
gemClient, GroqClient, CORE_API_KEY = Config.init_clients()

# Register routers
app.include_router(ui_router)
app.include_router(journal_router)
app.include_router(llm_router)
app.include_router(pipeline_router)
app.include_router(translation_router)


# Test routes
@app.get("/home")
def home():
    return {"message": "Automate the journals"}


@app.get("/about")
def aboutMe():
    return {
        "message": "This is a process where we are going to work with some Transformers APIs "
        "and that gonna lead us to automation (by webscraping and more.)"
    }