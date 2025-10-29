# File: Apps/config.py
from .library_import import (
    load_dotenv,
    os,
    StaticFiles,
    Jinja2Templates,
    FastAPI,
    genai,
    Groq,
)

# Load env vars
load_dotenv()

class Config:

    @staticmethod
    def init_clients():
        """Initialize Gemini and Groq clients."""
        gem_client = genai.Client(api_key=os.getenv("gemAPI1"))
        groq_client = Groq(api_key=os.getenv("groqAPI2"))
        CORE_API_KEY = os.getenv("coreAPI3")
        return gem_client, groq_client, CORE_API_KEY

    @staticmethod
    def create_app():
        """Initialize and return FastAPI app instance."""
        app = FastAPI(title="Pulsus PDF Generator")
        app.mount("/static", StaticFiles(directory="temp"), name="static")
        app.mount("/Logo", StaticFiles(directory="Apps/Logo"), name="Logo")
        app.templates = Jinja2Templates(directory="Apps/webTemplates")
        return app
