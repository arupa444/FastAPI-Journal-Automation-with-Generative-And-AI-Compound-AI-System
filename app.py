from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
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
import re
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
    prompt: Annotated[str, Field(..., title="Here, we can use Gemini", description="Enter prompt for the Gemini to compute....")]

class GroqRequest(BaseModel):
    prompt: Annotated[str, Field(..., title="Here, we can use Groq", description="Enter prompt for the Groq to compute....")]


class CoreRequest(BaseModel):
    prompt: Annotated[str, Field(..., title="Here, we can use Core for Research pages", description="Enter prompt for the Core to compute....")]










# class ContentItem(BaseModel):
#     subContent: str
#     references: str


# class ContentBlock(BaseModel):
#     content: dict[str, ContentItem]

# class PulsusOutputStr(BaseModel):
#     content:  Annotated[ContentBlock,Field(..., title="This is the content block", description="Enter the stacks in the content blocks....")]


class PulsusInputStr(BaseModel):
    id: Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    topic: Annotated[str, Field(..., title="Name of the topic", description="Enter the topic....")]
    journalName : Annotated[str, Field(..., title="Name of the journal where it belongs to.", description="Enter the journal where it belongs from...")]
    type: Annotated[str, Field(..., title="Name of the type(journal)", description="Enter the type of journal....")]
    citation : Annotated[str, Field(..., title="The citation of the journal", description="Enter the citation for this journal....")]
    author: Annotated[str, Field(..., title="Name of the author", description="Enter the author....")]
    email : Annotated[EmailStr, Field(..., title="Email of the author", description="Enter the autors email....")]
    authorsDepartment : Annotated[str, Field(..., title="Department of the authour", description="Enter the department of the author....")]
    received: Annotated[str, Field(..., title="The receiving date", description="Enter the receiving date in DD-Mon format....")]
    editorAssigned: Annotated[str, Field(..., title="The Editor Assigned date", description="Enter the editor assigned date in DD-Mon format....")]
    reviewed: Annotated[str, Field(..., title="The journal review date", description="Enter the journal review date in DD-Mon format....")]
    revised: Annotated[str, Field(..., title="The journal revised date", description="Enter the journal revised date in DD-Mon format....")]
    published: Annotated[str, Field(..., title="The publishing date of journal", description="Enter the publishing date of the journal in DD-Mon format....")]
    manuscriptNo : Annotated[str, Field(..., title="The manuscriptNo of this journal", description="Enter the manuscriptNo for this journal....")]
    volume: Annotated[int, Field(..., title="The volume for the issue", description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[int, Field(..., title="The issue no. of the volume", description="Enter the issue no. of the volume...",gt=0)]
    pdfNo: Annotated[int, Field(..., title="The pdf number", description="Enter the pdf number....",gt=0)]
    doi : Annotated[str, Field(..., title="DOI for this journal", description="Enter DOI for this Journal....")]
    ISSN : Annotated[str, Field(..., title="ISSN number of this journal", description="Enter the ISSN number for the journal....")]
    parentLink : Annotated[AnyUrl, Field(..., title="The url for the centralized link", description="Enter the link which will led to the centralized page....")]




    @field_validator('received', "editorAssigned", "reviewed", "revised", "published")
    @classmethod
    def validateDates(cls, value):
        months = {'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'}
        newVal = value.split("-")
        if len(newVal) != 3:
            raise ValueError("Enter Correct date formate DD-Mmm-YYYY")
        newVal[1] = newVal[1].capitalize()
        if newVal[1] not in months:
            raise ValueError("Enter the correct months['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']")
        if int(newVal[0])>31 or int(newVal[0])<1:
            raise ValueError("invalid date, keep that inbetween 1-31")
        value = '-'.join(newVal)
        return value
   
    @field_validator('pdfNo')
    @classmethod
    def validatePDFNo(cls, value):
        data = fetchInpData()
        for i in data.values():
            if value == i['pdfNo']:
                raise ValueError(f'Change the pdf page no. it is similar to the pdf artical name{i['topic']}')
        return value

class UpdateInputPartJournal(BaseModel):
    id: Annotated[Optional[str], Field(default=None, title="ID of the Input Journal", description="Enter the id for this journal input....")]
    topic: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    journalName : Annotated[Optional[str], Field(default=None, title="Name of the journal where it belongs to.", description="Enter the journal where it belongs from...")]
    type: Annotated[Optional[str], Field(default=None, title="Name of the type(journal)", description="Enter the type of journal....")]
    citation : Annotated[Optional[str], Field(default=None, title="The citation of the journal", description="Enter the citation for this journal....")]
    author: Annotated[Optional[str], Field(default=None, title="Name of the author", description="Enter the author....")]
    email : Annotated[Optional[EmailStr], Field(default=None, title="Email of the author", description="Enter the autors email....")]
    authorsDepartment : Annotated[Optional[str], Field(default=None, title="Department of the authour", description="Enter the department of the author....")]
    received: Annotated[Optional[str], Field(default=None, title="The receiving date", description="Enter the receiving date in DD-Mon format....")]
    editorAssigned: Annotated[Optional[str], Field(default=None, title="The Editor Assigned date", description="Enter the editor assigned date in DD-Mon format....")]
    reviewed: Annotated[Optional[str], Field(default=None, title="The journal review date", description="Enter the journal review date in DD-Mon format....")]
    revised: Annotated[Optional[str], Field(default=None, title="The journal revised date", description="Enter the journal revised date in DD-Mon format....")]
    published: Annotated[Optional[str], Field(default=None, title="The publishing date of journal", description="Enter the publishing date of the journal in DD-Mon format....")]
    manuscriptNo : Annotated[Optional[str], Field(default=None, title="The manuscriptNo of this journal", description="Enter the manuscriptNo for this journal....")]
    volume: Annotated[Optional[int], Field(default=None, title="The volume for the issue", description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[Optional[int], Field(default=None, title="The issue no. of the volume", description="Enter the issue no. of the volume...",gt=0)]
    pdfNo: Annotated[Optional[int], Field(default=None, title="The pdf number", description="Enter the pdf number....",gt=0)]
    doi : Annotated[Optional[str], Field(default=None, title="DOI for this journal", description="Enter DOI for this Journal....")]
    ISSN : Annotated[Optional[str], Field(default=None, title="ISSN number of this journal", description="Enter the ISSN number for the journal....")]
    parentLink : Annotated[Optional[AnyUrl], Field(default=None, title="The url for the centralized link", description="Enter the link which will led to the centralized page....")]



class ArticleItem(BaseModel):
    title: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    subContent: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    authors: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    published: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    doi: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    url: Annotated[Optional[AnyUrl], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    fulltextLinks: Annotated[Optional[List[str]], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    keywords: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    references: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]





class PulsusOutputStr(BaseModel):
    title :  Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    journalName : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    type :  Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    authors : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    email : Annotated[EmailStr, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    authorsDepartment : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    citation : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    journalYearVolumeIssue : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    introduction : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    description : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    content : Annotated[Dict[str, Dict], Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    doi : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    received : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    editorAssigned : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    reviewed : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    revised : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    published : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    year : Annotated[int, Field(..., title="Yes of publishing", description="Enter the journal publising year...")]
    manuscriptNo : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    QCNo : Annotated[str, Field(..., title="The QC number", description="Enter the QC number....")]
    preQCNo : Annotated[str, Field(..., title="The preQC number", description="Enter the preQC number....")]
    RManuNo : Annotated[str, Field(..., title="The RManuNo number", description="Enter the RManuNo number....")]
    volume: Annotated[int, Field(..., title="The volume for the issue", description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[int, Field(..., title="The issue no. of the volume", description="Enter the issue no. of the volume...",gt=0)]
    ISSN : Annotated[str, Field(..., title="ISSN Number", description="Enter the ISSN Number....")]
    parentLink : Annotated[AnyUrl, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    conclusion : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 

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

    


def fetchInpData():
    with open('journalDBInput.json','r') as file:
        data = json.load(file)
        return data
   


def saveInpData(data):
    with open('journalDBInput.json','w') as file:
        json.dump(data, file, default=str)





def fetchOutData():
    with open('journalDBOutput.json','r') as file:
        data = json.load(file)
        return data
   

def saveOutData(data):
    with open('journalDBOutput.json','w') as file:
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
def home():
    return {"message":"Automate the journals"}


@app.get("/about")
def aboutMe():
    return {"message":"This is a process where we are going to work with some Transformers APIs and that gonna lead us to a automation(by webscraping and more.)"}


@app.get("/view/journalInputData")
def viewTheData():
    data = fetchInpData()
    return f'{data}\n this is the journal data input.'


@app.get("/journalInputData/{JournalInputID}")
def fetchOneP(JournalInputID: str = Path(..., description='Enter your journal input index here....', example="J001",max_length=4)):
    data = fetchInpData()
    if JournalInputID in data:
        return data[JournalInputID]
    raise HTTPException(status_code=404, detail='JOurnal input not found in DB')

@app.post("/addJournalInInput")
def createJournal(pulsusInput : PulsusInputStr):
    data = fetchInpData()
    if pulsusInput.id in data:
        raise HTTPException(status_code=400, detail="The id is already there.")
    data[pulsusInput.id] = pulsusInput.model_dump(exclude=["id"])
    saveInpData(data)
    return JSONResponse(status_code=200, content="Data Added successfully")

@app.put("/updateInputJournal/{JournalInputID}")
def updateInpJournal(JournalInputID: str, updateJor : UpdateInputPartJournal):
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
   
    return JSONResponse(status_code=200,content={"message":"Successfully updated"})


@app.delete("/delete/journalInputData/{JournalInputID}")
def deletePatient(JournalInputID):
    data = fetchInpData()
    if JournalInputID not in data:
        raise HTTPException(status_code=404, detail="Journal Not Found")
   
    del data[JournalInputID]


    saveInpData(data)


    return JSONResponse(status_code=200, content={"message":f"Perfectly deleted the {JournalInputID}"})

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
def pulsus_ask_groq(LLaMAAAAAAA : GroqRequest):
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

    # Step 3: Create universal prompt
    prompt = f"""
    You are provided by a topic:
    topic : "{journal.topic}"


    Using this data, generate a summarized structure that contains only "subContent" (summary of key insights from the article) and "references" (citation-style reference).


    The final structure should look like:
    "content": {{
      "C001": {{
        "subContent": "...",
        "references": "...",
        "parentLink": "..." #parent link is the link where we can find the article or the journal
      }}, # try to achieve as much as possible but maximum will be 15(C015) and the minimum will be 10(C010)
      ...
    }}


    Ensure the summaries are meaningful and extracted from the provided article data.
    Focus on creating references from title, authors, year, and DOI if available.
    And also if possible add some more important ("article" and "journal") data on that topic from your side and merge it with the same thing.
    the most important the whole data will be copied out and used so give me clean information only the structured data no other thing not even a symbol or dot.
    note: Write like a confident, clear thinking human speaking to another smart human.
        Avoid robotic phrases like 'in today's fast-paced world', 'leveraging synergies', or
        'furthermore.
        Skip unnecessary dashes (-), quotation marks (''), and corporate buzzwords like 'cutting-edge', 'robust', or 'seamless experience. No Al tone. No fluff. No filler.
        Use natural transitions like 'here's the thing', ‘let's break it down; or ‘what this really means is’ Keep sentences varied in length and rhythm, like how real people speak or write. Prioritize clarity, personality, and usefulness.
        Every sentence should feel intentional, not generated
    """

    # Step 4: Ask Gemini
    try:
        gem_response = gemClient.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        gem_summary = gem_response.text
    except Exception as e:
        gem_summary = f"Gemini API failed: {str(e)}"

    # Step 5: Ask Groq
    try:
        chat_completion = GroqClient.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
        )
        groq_summary = chat_completion.choices[0].message.content
    except Exception as e:
        groq_summary = f"Groq API failed: {str(e)}"

    # Step 6: Clean and parse JSON output from Gemini or Groq
    raw_json = extract_json_from_markdown(gem_summary if "Gemini API failed" not in gem_summary else groq_summary)


    try:
        parsed = json.loads(raw_json)
        content_data = parsed["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse structured JSON from LLM output: {str(e)}")


    # Step 7: Conclusion content using Gemini
    prompt = f"""
    This is the given data : "{content_data}"
    i want to you to process this data and give me some output:
    1: Give me a brief summary from the given data where the word count lies in between 200 - 400.
    2: Give me a brief introduction from the given data where it will contain the citation markers as well, and you have to take in this way: the "C001" will be 1, "C002": 2......, where the word count lies in between 600 - 800.
    3: Give me a brief description from the given data where it will contain the citation markers as well, and you have to take in this way: the "C001" will be 1, "C002": 2......, where the word count lies in between 600 - 800.

    The final structure should look like:
    "content": {{
      "introduction": '''...''',
      "description" : '''...''',
      "summary" : '''...'''
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

    # Step 7.5: Clean and parse JSON output from Gemini or Groq
    raw_json = extract_json_from_markdown(gem_info)

    try:
        parsed = json.loads(raw_json)
        gem_info = parsed["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse structured JSON from LLM output: {str(e)}")




    # Step 8: Title content using Gemini
    prompt = f"give me a 5 to 7 words title based on the generated summary {content_data}. use playoff method to generate 5,6 titles and choose the best one and give that title. no need to display background process. just give 1 title as a final response"

    try:
        gem_response = gemClient.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        gem_title = gem_response.text
    except Exception as e:
        gem_title = f"Gemini API failed: {str(e)}"




    # Step 9: Final response
    final_output = {
        journal.id: {
            "title": gem_title,
            "journalName" : journal.journalName,
            "type": journal.type,
            "authors": journal.author,
            "email": journal.email,
            "authorsDepartment": journal.authorsDepartment,
            "citation": journal.citation,
            "journalYearVolumeIssue": f"{journal.journalName} {journal.published.split('-')[-1]} Volume {journal.volume} Issue {journal.issues}",
            "introduction": gem_info["introduction"] ,
            "description": gem_info["description"] ,
            "content": content_data,
            "doi": journal.doi,
            "received": journal.received,
            "editorAssigned": journal.editorAssigned,
            "reviewed": journal.reviewed,
            "revised": journal.revised,
            "published": journal.published,
            "year" : int(journal.published.split('-')[-1]),
            "manuscriptNo": journal.manuscriptNo,
            "QCNo": f"Q-{journal.manuscriptNo.split('-')[-1]}",
            "preQCNo": f"P-{journal.manuscriptNo.split('-')[-1]}",
            "RManuNo" : f"R-{journal.manuscriptNo.split('-')[-1]}",
            "volume" : journal.volume,
            "issues" : journal.issues,
            "ISSN" : journal.ISSN,
            "parentLink": str(journal.parentLink),
            "conclusion": gem_info["summary"]
        }
    }
    
    saveInpData(data)
    
    data = fetchOutData()
    pulsus_output_instance = PulsusOutputStr(**final_output[journal.id])
    data[journal.id] = pulsus_output_instance.model_dump()
    saveOutData(data)

    # ===== Load Jinja2 Template =====
    env = Environment(
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
        loader=FileSystemLoader(pathOfPathLib("."))  # current folder
    )

    template = env.get_template("finalFormate.tex")

    # ===== Render LaTeX =====
    rendered_latex = template.render(**data[journal.id])
    outputFileName = f"{journal.id}.tex"

    # ===== Save LaTeX to file =====
    tex_file = pathOfPathLib(outputFileName)
    tex_file.write_text(rendered_latex, encoding="utf-8")

    # ===== Compile LaTeX to PDF =====
    subprocess.run(["pdflatex", "-interaction=nonstopmode", str(tex_file)], check=True)

    return JSONResponse(status_code=200, content="Data Added successfull and generated PDF successfully✅.")
