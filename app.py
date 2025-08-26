from math import e
from fastapi import FastAPI, Path, HTTPException, Query, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import json
from pydantic import BaseModel, Field, field_validator, computed_field, AnyUrl, EmailStr
from typing import Annotated, Literal, Optional, List, Dict
import subprocess
from pathlib import Path as pathOfPathLib
from jinja2 import Environment, FileSystemLoader
from google import genai
from groq import Groq
import os
import httpx
import copy
import re
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv



load_dotenv()



# API section

gemClient = genai.Client(
    api_key=os.getenv('gemAPI1')
)

GroqClient = Groq(
    api_key=os.getenv('groqAPI2')
)

CORE_API_KEY = os.getenv('coreAPI3')

app = FastAPI()


class GeminiRequest(BaseModel):
    prompt: Annotated[
        str, Field(..., title="Here, we can use Gemini", description="Enter prompt for the Gemini to compute....")]


class GroqRequest(BaseModel):
    prompt: Annotated[
        str, Field(..., title="Here, we can use Groq", description="Enter prompt for the Groq to compute....")]


class CoreRequest(BaseModel):
    prompt: Annotated[str, Field(..., title="Here, we can use Core for Research pages",
                                 description="Enter prompt for the Core to compute....")]


# Template configuration
templates = Jinja2Templates(directory="webTemplates")


# class ContentItem(BaseModel):
#     subContent: str
#     references: str


# class ContentBlock(BaseModel):
#     content: dict[str, ContentItem]

# class PulsusOutputStr(BaseModel):
#     content:  Annotated[ContentBlock,Field(..., title="This is the content block", description="Enter the stacks in the content blocks....")]


class PulsusInputStr(BaseModel):
    id: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....",
                   max_length=6, min_length=3)]
    topic: Annotated[str, Field(..., title="Name of the topic", description="Enter the topic....")]
    journalName: Annotated[str, Field(..., title="Name of the journal where it belongs to.",
                                      description="Enter the journal where it belongs from...")]
    shortJournalName: Annotated[str, Field(..., title="Name of the short journal name where it belongs to.",
                                           description="Enter the short journal name where it belongs from...")]
    type: Annotated[str, Field(..., title="Name of the type(journal)", description="Enter the type of journal....")]
    author: Annotated[str, Field(..., title="Name of the author", description="Enter the author....")]
    email: Annotated[EmailStr, Field(..., title="Email of the author", description="Enter the autors email....")]
    brandName: Annotated[str, Field(..., title="Name of the brand", description="Enter the name of your brand...")]
    authorsDepartment: Annotated[
        str, Field(..., title="Department of the authour", description="Enter the department of the author....")]
    received: Annotated[
        str, Field(..., title="The receiving date", description="Enter the receiving date in DD-Mon format....")]
    editorAssigned: Annotated[str, Field(..., title="The Editor Assigned date",
                                         description="Enter the editor assigned date in DD-Mon format....")]
    reviewed: Annotated[str, Field(..., title="The journal review date",
                                   description="Enter the journal review date in DD-Mon format....")]
    revised: Annotated[str, Field(..., title="The journal revised date",
                                  description="Enter the journal revised date in DD-Mon format....")]
    published: Annotated[str, Field(..., title="The publishing date of journal",
                                    description="Enter the publishing date of the journal in DD-Mon format....")]
    manuscriptNo: Annotated[str, Field(..., title="The manuscriptNo of this journal",
                                       description="Enter the manuscriptNo for this journal....")]
    volume: Annotated[
        int, Field(..., title="The volume for the issue", description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[
        int, Field(..., title="The issue no. of the volume", description="Enter the issue no. of the volume...", gt=0)]
    pdfNo: Annotated[int, Field(..., title="The pdf number", description="Enter the pdf number....", gt=0)]
    doi: Annotated[str, Field(..., title="DOI for this journal", description="Enter DOI for this Journal....")]
    ISSN: Annotated[
        str, Field(..., title="ISSN number of this journal", description="Enter the ISSN number for the journal....")]
    imgPath: Annotated[Optional[str], Field(default=None, title="image path", description="Enter the img path....")]
    parentLink: Annotated[AnyUrl, Field(..., title="The url for the centralized link",
                                        description="Enter the link which will led to the centralized page....")]

    @field_validator('received', "editorAssigned", "reviewed", "revised", "published")
    @classmethod
    def validateDates(cls, value):
        months = {'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'}
        newVal = value.split("-")
        if len(newVal) != 3:
            raise ValueError("Enter Correct date formate DD-Mmm-YYYY")
        newVal[1] = newVal[1].capitalize()
        if newVal[1] not in months:
            raise ValueError(
                "Enter the correct months['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']")
        if int(newVal[0]) > 31 or int(newVal[0]) < 1:
            raise ValueError("invalid date, keep that inbetween 1-31")
        value = '-'.join(newVal)
        return value

    @field_validator('pdfNo')
    @classmethod
    def validatePDFNo(cls, value):
        data = fetchInpData()
        for i in data.values():
            if value == i['pdfNo']:
                raise ValueError(f"Change the pdf page no. it is similar to the pdf artical name{i['topic']}")
        return value

    @computed_field
    @property
    def citeAuthorFormate(self) -> str:
        if self.brandName == 'hilaris.tex':
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 to 6 authors and seperated with comma). title of that journal inside double quotation. Journal short name. Volume of the journal (year of publishing inside parenthesis):the page range or the number.end it with a full stop (for example: 'author n, author n, author n. "titleOFtheJournal". journalShortName. Volume (year):ThePageRangeOrTheNumber.')"""

        if self.brandName == 'alliedAcademy.tex':
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 or less not more authors then that and seperated with comma), title of that journal, Journal short name. year of publishing;Volume of the journal:the page range or the number.(for example: 'author n, author n, author n, titleOFtheJournal, journalShortName. year;Volume:ThePageRangeOrTheNumber')"""

        if self.brandName == 'omics.tex':
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 to 6 authors and seperated with comma) (year of publishing inside parenthesis) title of that journal. Journal short name Volume of the journal:the page range or the number.(for example: 'author n, author n, author n (year) titleOFtheJournal. journalShortName Volume:ThePageRangeOrTheNumber')"""


class UpdateInputPartJournal(BaseModel):
    id: Annotated[Optional[str], Field(default=None, title="ID of the Input Journal",
                                       description="Enter the id for this journal input....")]
    topic: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    journalName: Annotated[Optional[str], Field(default=None, title="Name of the journal where it belongs to.",
                                                description="Enter the journal where it belongs from...")]
    shortJournalName: Annotated[
        Optional[str], Field(default=None, title="Name of the short journal name where it belongs to.",
                             description="Enter the short journal name where it belongs from...")]
    type: Annotated[Optional[str], Field(default=None, title="Name of the type(journal)",
                                         description="Enter the type of journal....")]
    author: Annotated[
        Optional[str], Field(default=None, title="Name of the author", description="Enter the author....")]
    email: Annotated[
        Optional[EmailStr], Field(default=None, title="Email of the author", description="Enter the autors email....")]
    brandName: Annotated[
        Optional[str], Field(default=None, title="Name of the brand", description="Enter the name of your brand...")]
    authorsDepartment: Annotated[Optional[str], Field(default=None, title="Department of the authour",
                                                      description="Enter the department of the author....")]
    received: Annotated[Optional[str], Field(default=None, title="The receiving date",
                                             description="Enter the receiving date in DD-Mon format....")]
    editorAssigned: Annotated[Optional[str], Field(default=None, title="The Editor Assigned date",
                                                   description="Enter the editor assigned date in DD-Mon format....")]
    reviewed: Annotated[Optional[str], Field(default=None, title="The journal review date",
                                             description="Enter the journal review date in DD-Mon format....")]
    revised: Annotated[Optional[str], Field(default=None, title="The journal revised date",
                                            description="Enter the journal revised date in DD-Mon format....")]
    published: Annotated[Optional[str], Field(default=None, title="The publishing date of journal",
                                              description="Enter the publishing date of the journal in DD-Mon format....")]
    manuscriptNo: Annotated[Optional[str], Field(default=None, title="The manuscriptNo of this journal",
                                                 description="Enter the manuscriptNo for this journal....")]
    volume: Annotated[Optional[int], Field(default=None, title="The volume for the issue",
                                           description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[Optional[int], Field(default=None, title="The issue no. of the volume",
                                           description="Enter the issue no. of the volume...", gt=0)]
    pdfNo: Annotated[
        Optional[int], Field(default=None, title="The pdf number", description="Enter the pdf number....", gt=0)]
    doi: Annotated[
        Optional[str], Field(default=None, title="DOI for this journal", description="Enter DOI for this Journal....")]
    ISSN: Annotated[Optional[str], Field(default=None, title="ISSN number of this journal",
                                         description="Enter the ISSN number for the journal....")]
    imgPath: Annotated[Optional[str], Field(default=None, title="image path", description="Enter the img path....")]
    parentLink: Annotated[Optional[AnyUrl], Field(default=None, title="The url for the centralized link",
                                                  description="Enter the link which will led to the centralized page....")]


class ArticleItem(BaseModel):
    title: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    subContent: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    authors: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    published: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    doi: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    url: Annotated[Optional[AnyUrl], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    fulltextLinks: Annotated[
        Optional[List[str]], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    keywords: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    references: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]


class PulsusOutputStr(BaseModel):
    title: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    journalName: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    shortJournalName: Annotated[str, Field(..., title="Name of the short journal name where it belongs to.",
                                           description="Enter the short journal name where it belongs from...")]
    type: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    author: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    email: Annotated[
        EmailStr, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    brandName: Annotated[str, Field(..., title="Name of the brand", description="Enter the name of your brand...")]
    authorsDepartment: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    journalYearVolumeIssue: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    introduction: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    description: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    content: Annotated[Dict[str, Dict], Field(..., title="ID of the Input Journal",
                                              description="Enter the id for this journal input....")]
    abstract: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    doi: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    received: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    editorAssigned: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    reviewed: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    revised: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    published: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    year: Annotated[int, Field(..., title="Yes of publishing", description="Enter the journal publising year...")]
    manuscriptNo: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    QCNo: Annotated[str, Field(..., title="The QC number", description="Enter the QC number....")]
    preQCNo: Annotated[str, Field(..., title="The preQC number", description="Enter the preQC number....")]
    RManuNo: Annotated[str, Field(..., title="The RManuNo number", description="Enter the RManuNo number....")]
    volume: Annotated[
        int, Field(..., title="The volume for the issue", description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[
        int, Field(..., title="The issue no. of the volume", description="Enter the issue no. of the volume...", gt=0)]
    ISSN: Annotated[Optional[str], Field(default="", title="ISSN Number", description="Enter the ISSN Number....")]
    imgPath: Annotated[Optional[str], Field(default=None, title="image path", description="Enter the img path....")]
    pdfNo: Annotated[Optional[int], Field(..., title="Pdf Number", description="Enter the PDF Number....")]
    parentLink: Annotated[
        AnyUrl, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    conclusion: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]

    @field_validator('content')
    @classmethod
    def validatePDFNo(cls, value):
        # Avoid modifying dict during iteration
        keys_to_delete = []
        for i, j in value.items():
            if j.get('subContent') is None or j.get('references') is None:
                keys_to_delete.append(i)
        for k in keys_to_delete:
            del value[k]
        return value



    @computed_field
    @property
    def citation(self) -> str:
        if self.brandName == 'hilaris.tex':
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            justToCite[0] = f"{justToCite[0]},"
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite}. "{self.title}." {self.shortJournalName} {self.volume} ({self.published.split("-")[-1]}):{self.pdfNo}."""

        if self.brandName == 'alliedAcademy.tex':
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"{justToCite}. {self.title}. {self.shortJournalName}. {self.published.split("-")[-1]};{self.volume}({self.issues}):{self.pdfNo}."

        if self.brandName == 'omics.tex':
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"{justToCite},({self.published.split("-")[-1]}) {self.title}. {self.shortJournalName} {self.volume}: {self.pdfNo}. DOI: {self.doi}"




def fetchInpData():
    if not os.path.exists('journalDBInput.json'):
        return {}  # File doesn't exist → return empty dict

    with open('journalDBInput.json', 'r') as file:
        try:
            data = json.load(file)
            if not isinstance(data, dict):  # Ensure it's a dict
                return {}
            return data
        except json.JSONDecodeError:
            # File exists but is empty or invalid JSON
            return {}


def saveInpData(data):
    with open('journalDBInput.json', 'w') as file:
        if data is None:
            file = {}
        json.dump(data, file, default=str)


def fetchOutData():
    if not os.path.exists('journalDBOutput.json'):
        return {}  # File doesn't exist → return empty dict

    with open('journalDBOutput.json', 'r') as file:
        try:
            data = json.load(file)
            if not isinstance(data, dict):  # Ensure it's a dict
                return {}
            return data
        except json.JSONDecodeError:
            # File exists but is empty or invalid JSON
            return {}


def saveOutData(data):
    with open('journalDBOutput.json', 'w') as file:
        if data is None:
            file = {}
        json.dump(data, file, default=str)


def sanitize_for_json(obj):
    """Convert objects like AnyUrl into plain serializable types."""
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, AnyUrl):
        return str(obj)
    return obj


def extract_json_from_markdown(text: str) -> str:
    """Extract JSON block from LLM markdown-style response."""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


@app.get("/")
def ui_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ui/about")
def ui_about(request: Request):
    return templates.TemplateResponse("aboutUs.html", {"request": request})


@app.get("/ui/add-journal")
def ui_add_journal(request: Request):
    return templates.TemplateResponse("addJournal.html", {"request": request})


@app.get("/ui/update-journal")
def ui_update_journal(request: Request):
    return templates.TemplateResponse("updateJournal.html", {"request": request})


@app.get("/ui/ask-gemini")
def ui_ask_gemini(request: Request):
    return templates.TemplateResponse("askGemini.html", {"request": request})


@app.get("/ui/ask-groq")
def ui_ask_groq(request: Request):
    return templates.TemplateResponse("askGroq.html", {"request": request})


@app.get("/ui/core-search")
def ui_core_search(request: Request):
    return templates.TemplateResponse("coreSearch.html", {"request": request})


app.mount("/Logo", StaticFiles(directory="Logo"), name="Logo")


@app.get("/ui/pipeline")
def ui_pipeline(request: Request):
    image_files = []
    # Allowed image extensions
    allowed_ext = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg")

    for filename in os.listdir("Logo"):
        if filename.lower().endswith(allowed_ext):
            image_files.append(filename)

    return templates.TemplateResponse(
        "pipeline.html",
        {"request": request, "images": image_files}
    )


@app.get("/ui/delete-journal")
def ui_delete_journal(request: Request):
    return templates.TemplateResponse("deleteJournal.html", {"request": request})


@app.get("/home")
def home():
    return {"message": "Automate the journals"}


@app.get("/about")
def aboutMe():
    return {
        "message": "This is a process where we are going to work with some Transformers APIs and that gonna lead us to a automation(by webscraping and more.)"}


@app.get("/view/journalInputData")
def viewTheData():
    data = fetchInpData()
    return f'{data}\n this is the journal data input.'


@app.get("/journalInputData/{JournalInputID}")
def fetchOneP(JournalInputID: str = Path(..., description='Enter your journal input index here....', example="J001",
                                         max_length=4)):
    data = fetchInpData()
    if JournalInputID in data:
        return data[JournalInputID]
    raise HTTPException(status_code=404, detail='JOurnal input not found in DB')


@app.post("/addJournalInInput")
def createJournal(pulsusInput: PulsusInputStr):
    data = fetchInpData()
    if pulsusInput.id in data:
        raise HTTPException(status_code=400, detail="The id is already there.")
    data[pulsusInput.id] = pulsusInput.model_dump(exclude=["id"])
    saveInpData(data)
    return JSONResponse(status_code=200, content="Data Added successfully")


@app.put("/updateInputJournal/{JournalInputID}")
def updateInpJournal(JournalInputID: str, updateJor: UpdateInputPartJournal):
    data = fetchInpData()

    if JournalInputID not in data:
        raise HTTPException(status_code=404, detail="Journal Input not found")

    tempStoreInfo = data[JournalInputID]
    tempStoreInfo["id"] = JournalInputID

    updatedInfo = updateJor.model_dump(exclude_unset=True)

    for key, value in updatedInfo.items():
        tempStoreInfo[key] = value

    validateInpJournal = UpdateInputPartJournal(**tempStoreInfo)

    data[JournalInputID] = validateInpJournal.model_dump(exclude=['id'])
    saveInpData(data)

    return JSONResponse(status_code=200, content={"message": "Successfully updated"})


@app.delete("/delete/journalInputData/{JournalInputID}")
def deletePatient(JournalInputID):
    data = fetchInpData()
    if JournalInputID not in data:
        raise HTTPException(status_code=404, detail="Journal Not Found")

    del data[JournalInputID]

    saveInpData(data)

    return JSONResponse(status_code=200, content={"message": f"Perfectly deleted the {JournalInputID}"})


@app.post("/pulsus-ask-gemini")
def pulsus_ask_gemini(gem: GeminiRequest):
    try:
        response = gemClient.models.generate_content(
            model="gemini-2.5-flash", contents=gem.prompt
        )
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")


@app.post("/pulsus-ask-groq")
def pulsus_ask_groq(LLaMAAAAAAA: GroqRequest):
    try:
        chat_completion = GroqClient.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": LLaMAAAAAAA.prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        return {"response": chat_completion.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")


def build_structured_content(results):
    content = {}
    for idx, item in enumerate(results.get("results", []), start=1):
        key = f"C{str(idx).zfill(3)}"

        title = item.get("title", "No title available")
        abstract = item.get("abstract", "No abstract available.")
        authors = ", ".join([a.get("name", "Unknown") for a in item.get("authors", [])]) or "Unknown author(s)"
        published_date = item.get("published", "Unknown date")
        doi = item.get("doi", "DOI not available")
        url = item.get("url", "https://URLNotAvailable")
        fulltext_links = item.get("fulltextUrls", [])
        subjects = ", ".join(item.get("topics", [])) if item.get("topics") else "No keywords"
        source = item.get("source", {}).get("name", "Unknown source")
        references = f"{authors} ({published_date}). {title}. {source}. DOI: {doi}"

        content[key] = {
            "title": title,
            "subContent": abstract,
            "authors": authors,
            "published": published_date,
            "doi": doi,
            "url": url,
            "fulltextLinks": fulltext_links,
            "keywords": subjects,
            "references": references
        }
        tempStoreContentForAuth = ArticleItem(**content[key])
        content[key] = tempStoreContentForAuth.model_dump()

    return {"content": content}


@app.post("/core/search/articles")
async def search_articles(core_req: CoreRequest):
    CORE_API_URL = "https://api.core.ac.uk/v3/search/works"
    headers = {
        "Authorization": f"Bearer {CORE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "q": core_req.prompt,
        "limit": 20
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:  # set timeout explicitly
            response = await client.post(CORE_API_URL, json=data, headers=headers)
            response.raise_for_status()

            try:
                results = response.json()
            except Exception as json_err:
                raise HTTPException(status_code=500, detail=f"Invalid JSON in response: {str(json_err)}")

            return build_structured_content(results)

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"CORE API returned HTTP error: {e.response.text}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@app.post("/pipeline/journal-full-process")
async def full_journal_pipeline(journal: PulsusInputStr):
    # Step 1: Save journal input
    data = fetchInpData()
    if journal.id in data:
        raise HTTPException(status_code=400, detail="Journal ID already exists.")
    data[journal.id] = journal.model_dump(exclude=["id"])

    print("step 1 : Save journal input ✅")

    # # Step 2: Use the topic to search CORE articles
    # CORE_API_URL = "https://api.core.ac.uk/v3/search/works"
    # headers = {
    #     "Authorization": f"Bearer {CORE_API_KEY}",
    #     "Content-Type": "application/json"
    # }
    # data = {
    #     "q": journal.topic,
    #     "limit": 1000
    # }

    # try:
    #     async with httpx.AsyncClient(timeout=15.0) as client:  # set timeout explicitly
    #         response = await client.post(CORE_API_URL, json=data, headers=headers)
    #         response.raise_for_status()

    #         try:
    #             results = response.json()
    #         except Exception as json_err:
    #             raise HTTPException(status_code=500, detail=f"Invalid JSON in response: {str(json_err)}")

    #         core_content_json = build_structured_content(results)

    # except httpx.HTTPStatusError as e:
    #     raise HTTPException(status_code=e.response.status_code,
    #                         detail=f"CORE API returned HTTP error: {e.response.text}")

    # except httpx.RequestError as e:
    #     raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    print("step 2 : Use the topic to search CORE articles ✅")

    # Step 3: Create universal prompt
    prompt = f"""
    You are provided by a topic:
    topic : "{journal.topic}"


    Using this topic, generate a summarized structure that contains "subContent" (summary of key insights from the article), "references" (citation-style reference) and the remainings and make sure all the journals are authentic not created by you and have more then or equal to 3 authors, and i need recent year data's(last 5 years) and must from a legit author and the links must work properly, don't provide any dummy data or dummy link.


    The final structure should look like:
    "content": {{
      "C001": {{
        "subContent": "...",
        "references": "...", # make sure that cite should be in {journal.citeAuthorFormate} formate
        "title": "...",
        "authors": ["...", "...", "..."], #only three authors name (full name)
        "published": "...",
        "pageRangeOrNumber": "...", #the page range or the page number
        "volume": "...",
        "issues": "...",
        "DOI": "...",
        "url": "...",
        "parentLink": "..."
      }}, # try to achieve the maximum of 10 (C010) counts.
      ...
    }}


    Focus on creating references from title, authors, year, and DOI.
    the most important thing, and the whole data will be copied out and used so give me clean information only the structured data no other thing not even a symbol or dot.
    note: Write like a confident, clear thinking human speaking to another smart human.
        Avoid robotic phrases like 'in today's fast-paced world', 'leveraging synergies', or
        'furthermore.
        Skip unnecessary dashes (-), quotation marks (''), and corporate buzzwords like 'cutting-edge', 'robust', or 'seamless experience. No Al tone. No fluff. No filler.
        Use natural transitions like 'here's the thing', 'let's break it down; or 'what this really means is' Keep sentences varied in length and rhythm, like how real people speak or write. Prioritize clarity, personality, and usefulness.
        Every sentence should feel intentional, not generated
    """
    print("step 3 : Create universal prompt ✅")
    # Step 4: Ask Gemini
    try:
        gem_response = gemClient.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        gem_summary = gem_response.text
    except Exception as e:
        gem_summary = f"Gemini API failed: {str(e)}"

    print("step 4 : ask Gemini ✅")

    # Step 5: Clean and parse JSON output from Gemini
    raw_json = extract_json_from_markdown(gem_summary)

    try:
        parsed = json.loads(raw_json)
        content_data = parsed["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse structured JSON from LLM output: {str(e)}")

    for kk in content_data.keys():
        store = []
        for i in content_data[kk]["authors"]:
            justToCite = i.split(' ')
            if len(justToCite) != 1:
                for i in range(1, len(justToCite)):
                    justToCite[i] = justToCite[i][0]
                justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            store.append(justToCite)
        content_data[kk]["authors"] = ", ".join(store)


    print("step 5 : Clean and parse JSON output from Gemini ✅")

    # Step 6: Conclusion content using Gemini
    prompt = f"""
    This is the given data : "{content_data}"
    i want to you to process this data and give me some output:
    1: Give me a brief summary from the given data where the word count lies in between 200 - 400.
    2: Give me a brief introduction from the given data where it will contain the citation markers as well, and note, you have to take in this way: the "C001" will be 1, "C002": 2...... and each section should have different but sequencial citation markers (for ex: "C001" will be 1, "C002": 2 and so on). and give two linebreak '\n' after the citation marker and also make sure the citation marker must stays before the full stop '.', and the full introduction word count lies in between 600 - 800.
    3: Give me a brief description from the given data and note, the full description contain more then 4 paragraphs with word count lies in between 600 - 800.
    4: Give me a abstract from the given data, and the full abstract word count lies in between 90 - 100.

    The final structure should look like:
    "content": {{
      "introduction": '''...''',
      "description" : '''...''',
      "summary" : '''...''',
      "abstract" : '''...'''
      ...
    }}


    note: Do not include any introductory labels, brand names, or meta-commentary. Remove all special characters, escape sequences, and formatting symbols. Respond only with plain and clean text containing the summary. Respond without any introductory phrases, labels, brand mentions, or headings (e.g., 'Summary:', 'Gemini:', 'Groq:'). Do not include explanations of how you generated the answer unless explicitly asked.
        Write like a confident, clear thinking human speaking to another smart human.
        Avoid robotic phrases like 'in today's fast-paced world', 'leveraging synergies', 'furthermore'.....
        Skip unnecessary dashes (-), quotation marks (''), and corporate buzzwords like 'cutting-edge', 'robust', or 'seamless experience. No Al tone. No fluff. No filler.
        Use natural transitions like 'here's the thing', ‘let's break it down; or ‘what this really means is’ Keep sentences varied in length and rhythm, like how real people speak or write. Prioritize clarity, personality, and usefulness.
        Every sentence should feel intentional, not generated
"""
    try:
        gem_response = gemClient.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        gem_info = gem_response.text
    except Exception as e:
        gem_info = f"Gemini API failed: {str(e)}"

    print("step 6 : Conclusion content using Gemini ✅")

    # Step 6.5: Clean and parse JSON output from Gemini or Groq
    raw_json = extract_json_from_markdown(gem_info)

    try:
        parsed = json.loads(raw_json)
        gem_info = parsed["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse structured JSON from LLM output: {str(e)}")

    print("step 6.5 : Clean and parse JSON output from Gemini or Groq ✅")

    # Step 7: Title content using Gemini
    prompt = f"give me a 5 to 7 words title based on the generated summary {content_data}. use playoff method to generate 5,6 titles and choose the best one and give that title. no need to display background process. just give 1 title as a final response"

    try:
        gem_response = gemClient.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        gem_title = gem_response.text
    except Exception as e:
        gem_title = f"Gemini API failed: {str(e)}"

    print("step 7 : Title content using Gemini ✅")

    # Step 8: Final response
    final_output = {
        journal.id: {
            "title": gem_title,
            "journalName": journal.journalName,
            "shortJournalName": journal.shortJournalName,
            "type": journal.type,
            "author": journal.author,
            "email": journal.email,
            "brandName": journal.brandName,
            "authorsDepartment": journal.authorsDepartment,
            "journalYearVolumeIssue": f"{journal.shortJournalName}, Volume {journal.volume}:{journal.issues}, {journal.published.split('-')[-1]}",
            "introduction": gem_info["introduction"],
            "description": gem_info["description"],
            "abstract": gem_info["abstract"],
            "content": content_data,
            "doi": journal.doi,
            "received": journal.received,
            "editorAssigned": journal.editorAssigned,
            "reviewed": journal.reviewed,
            "revised": journal.revised,
            "published": journal.published,
            "year": int(journal.published.split('-')[-1]),
            "manuscriptNo": journal.manuscriptNo,
            "QCNo": f"Q-{journal.manuscriptNo.split('-')[-1]}" if journal.brandName == "hilaris.tex" else journal.manuscriptNo,
            "preQCNo": f"P-{journal.manuscriptNo.split('-')[-1]}" if journal.brandName == "hilaris.tex" else journal.manuscriptNo,
            "RManuNo": f"R-{journal.manuscriptNo.split('-')[-1]}" if journal.brandName == "hilaris.tex" else journal.manuscriptNo,
            "volume": journal.volume,
            "issues": journal.issues,
            "pdfNo": journal.pdfNo,
            "ISSN": journal.ISSN,
            "imgPath": journal.imgPath,
            "parentLink": str(journal.parentLink),
            "conclusion": gem_info["summary"]
        }
    }

    saveInpData(data)

    output_data = fetchOutData()
    pulsus_output_instance = PulsusOutputStr(**final_output[journal.id])
    output_data[journal.id] = pulsus_output_instance.model_dump()
    saveOutData(output_data)

    # =========================================================================
    # File Generation Section
    # =========================================================================

    # --- Centralized Directory Setup ---
    # Create a single directory for all of this journal's output files.
    output_base_dir = pathOfPathLib("PDFStorePulsus")
    journal_folder = output_base_dir / journal.id
    journal_folder.mkdir(parents=True, exist_ok=True)

    print("step 8 : Final response ✅")

    # --- 9: Create HTML file ---
    env_html = Environment(
        loader=FileSystemLoader(pathOfPathLib("./templates/"))
    )
    try:
        html_template = env_html.get_template("Format1.html")
        forHtml = copy.deepcopy(output_data[journal.id])

        # Logic for processing references for HTML
        for i in range(1, len(forHtml["content"]) + 1):
            forHtml["introduction"] = forHtml["introduction"].replace(f"[{i}].",
                                                                      f"[<a href='#{i}' title='{i}'>{i}</a>].</p><p>")

        forHtml["description"] = forHtml["description"].replace("\n\n", "</p><p>")
        forHtml["description"] = forHtml["description"].replace("\n", "</p><p>")

        count = 0
        forHtml["storeRefPart"] = ""
        for i in forHtml["content"].values():
            count += 1
            i["issues"] = f"({i['issues']})" if i.get("issues") else ""

            temp = f"""<li><a name="{count}" id="{count}"></a>{i["authors"]} <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>. {i["published"]};{i["volume"]}{i["issues"]}:{i["pageRangeOrNumber"]}.</li>
            <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""

            forHtml["storeRefPart"] = f"""{forHtml['storeRefPart']}\n{temp}"""

        department_parts = forHtml['authorsDepartment'].split(',')
        if len(department_parts) > 1:
            forHtml["prefixAuthorDepartment"] = f"{department_parts[0]}<br />"
            forHtml["suffixAuthorDepartment"] = f"{','.join(department_parts[1:])}.<br />"
        else:
            forHtml["prefixAuthorDepartment"] = forHtml['authorsDepartment']
            forHtml["suffixAuthorDepartment"] = ""

        rendered_html = html_template.render(**forHtml)

        # Save the HTML file inside the journal's dedicated folder
        html_file_path = journal_folder / f"{journal.id}.html"
        html_file_path.write_text(rendered_html, encoding="utf-8")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate HTML file: {str(e)}")

    print("step 9 : Create HTML file ✅")

    # --- 10: Create PDF file ---
    env_latex = Environment(
        block_start_string=r'\BLOCK{',
        block_end_string='}',
        variable_start_string=r'\VAR{',
        variable_end_string='}',
        comment_start_string=r'\#{',
        comment_end_string='}',
        line_statement_prefix='%%',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=FileSystemLoader(pathOfPathLib("./templates"))
    )

    def latex_escape(text):
        if not isinstance(text, str):
            return text
        replacements = {'&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}',
                        '^': r'\^{}', }
        pattern = re.compile('|'.join(re.escape(k) for k in replacements.keys()))
        return pattern.sub(lambda m: replacements[m.group()], text)

    env_latex.filters['latex_escape'] = latex_escape
    template = env_latex.get_template(journal.brandName)

    rendered_latex = template.render(**output_data[journal.id])

    # Save the .tex file inside the journal's dedicated folder
    tex_file_path = journal_folder / f"{journal.id}.tex"
    tex_file_path.write_text(rendered_latex, encoding="utf-8")

    # Compile LaTeX to PDF. Run from within the journal's folder.
    for i in range(2):
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", tex_file_path.name],
            capture_output=True,  # Capture stdout/stderr
            text=True,
            cwd=journal_folder  # CRITICAL: Set the working directory
        )

        if result.returncode != 0:
            log_file_path = tex_file_path.with_suffix(".log")

            # The log file is already saved by xelatex, so we just read it for the error message
            error_text = "Unknown LaTeX error. Check the log file."
            if log_file_path.exists():
                with open(log_file_path, 'r') as f:
                    lines = f.readlines()
                error_snippets = [line for line in lines if line.startswith("! ")]
                error_text = "\n".join(error_snippets) or f"LaTeX compilation failed. Full log in {log_file_path}"

            raise HTTPException(
                status_code=500,
                detail=f"LaTeX compilation failed on run {i + 1}:\n\n{error_text}"
            )

    print("step 10 : Create PDF file ✅")

    return JSONResponse(
        status_code=200,
        content={"Status": f"Data added and files generated successfully in PDFStorePulsus/{journal.id}/ ✅."}
    )

