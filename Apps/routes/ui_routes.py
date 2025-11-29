from Apps.library_import import (
    Request,
    APIRouter,
    os,
    uuid,
    subprocess,
)
from Apps.config import Config
from Apps.models_journal import LatexRequest
from Apps.language_fonts import languages

app = Config.create_app()
templates = Config.create_app().templates
router = APIRouter()


@router.get("/")
def ui_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/ui/about")
def ui_about(request: Request):
    return templates.TemplateResponse("aboutUs.html", {"request": request})


@router.get("/ui/add-journal")
def ui_add_journal(request: Request):
    allowed_ext = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg")
    image_files = [
        f
        for f in os.listdir(
            "Apps/Logo"
        )
        if f.lower().endswith(allowed_ext)
    ]
    return templates.TemplateResponse(
        "addJournal.html", {
            "request": request, "images": image_files
        }
    )


@router.get("/ui/update-journal")
def ui_update_journal(request: Request):
    return templates.TemplateResponse("updateJournal.html", {"request": request})


@router.get("/ui/ask-gemini")
def ui_ask_gemini(request: Request):
    return templates.TemplateResponse("askGemini.html", {"request": request})


@router.get("/ui/ask-groq")
def ui_ask_groq(request: Request):
    return templates.TemplateResponse("askGroq.html", {"request": request})


@router.get("/ui/core-search")
def ui_core_search(request: Request):
    return templates.TemplateResponse("coreSearch.html", {"request": request})


@router.get("/ui/pipeline")
def ui_pipeline(request: Request):
    allowed_ext = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg")
    image_files = [
        f
        for f in os.listdir(
            "Apps/Logo"
        )
        if f.lower().endswith(allowed_ext)
    ]
    return templates.TemplateResponse(
        "pipeline.html", {"request": request, "images": image_files}
    )


@router.get("/ui/translate")
def ui_translate(request: Request):

    return templates.TemplateResponse(
        "translate.html", {"request": request, "languages": languages}
    )


@router.get("/ui/delete-journal")
def ui_delete_journal(request: Request):
    return templates.TemplateResponse("deleteJournal.html", {"request": request})


# PDF compilation route
@router.post("/compile-latex")
def compile_latex(req: LatexRequest):
    job_id = str(uuid.uuid4())
    tex_file = f"temp/{job_id}.tex"
    pdf_file = f"temp/{job_id}.pdf"

    os.makedirs("temp", exist_ok=True)
    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(req.source)

    try:
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-output-directory=temp", tex_file],
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr}

    return {"pdf_path": f"/static/{job_id}.pdf"}
