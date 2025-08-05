from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, field_validator, computed_field, AnyUrl, EmailStr
from typing import Annotated, Literal, Optional, List, Dict

from google import genai
from groq import Groq
import os
import httpx
import re
from dotenv import load_dotenv

import uvicorn 

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










class ContentItem(BaseModel):
    subContent: str
    references: str


class ContentBlock(BaseModel):
    content: dict[str, ContentItem]

class PulsusOutputStr(BaseModel):
    content:  Annotated[ContentBlock,Field(..., title="This is the content block", description="Enter the stacks in the content blocks....")]


class PulsusInputStr(BaseModel):
    id: Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    topic: Annotated[str, Field(..., title="Name of the topic", description="Enter the topic....")]
    type: Annotated[str, Field(..., title="type of the topic", description="Enter the type....")]
    author: Annotated[str, Field(..., title="Name of the author", description="Enter the author....")]
    received: Annotated[str, Field(..., title="The receiving date", description="Enter the receiving date in DD-Mon format....")]
    editorAssigned: Annotated[str, Field(..., title="The Editor Assigned date", description="Enter the editor assigned date in DD-Mon format....")]
    reviewed: Annotated[str, Field(..., title="The journal review date", description="Enter the journal review date in DD-Mon format....")]
    revised: Annotated[str, Field(..., title="The journal revised date", description="Enter the journal revised date in DD-Mon format....")]
    published: Annotated[str, Field(..., title="The publishing date of journal", description="Enter the publishing date of the journal in DD-Mon format....")]
    generalName: Annotated[str, Field(..., title="The general name of volume", description="Enter the general name of the volume....")]
    keyword: Annotated[List, Field(..., title="The keywords for this issues", description="Enter the keywords for this issues....")]
    volume: Annotated[int, Field(..., title="The volume for the issue", description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[int, Field(..., title="The issue no. of the volume", description="Enter the issue no. of the volume...",gt=0)]
    pdfNo: Annotated[int, Field(..., title="The pdf number", description="Enter the pdf number....",gt=0)]
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
    topic: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    type: Annotated[Optional[str], Field(default=None, title="type of the topic", description="Enter the type....")]
    author: Annotated[Optional[str], Field(default=None, title="Name of the author", description="Enter the author....")]
    received: Annotated[Optional[str], Field(default=None, title="The receiving date", description="Enter the receiving date in DD-Mon format....")]
    editorAssigned: Annotated[Optional[str], Field(default=None, title="The Editor Assigned date", description="Enter the editor assigned date in DD-Mon format....")]
    reviewed: Annotated[Optional[str], Field(default=None, title="The journal review date", description="Enter the journal review date in DD-Mon format....")]
    revised: Annotated[Optional[str], Field(default=None, title="The journal revised date", description="Enter the journal revised date in DD-Mon format....")]
    published: Annotated[Optional[str], Field(default=None, title="The publishing date of journal", description="Enter the publishing date of the journal in DD-Mon format....")]
    generalName: Annotated[Optional[str], Field(default=None, title="The general name of volume", description="Enter the general name of the volume....")]
    keyword: Annotated[Optional[List], Field(..., title="The keywords for this issues", description="Enter the keywords for this issues....")]
    volume: Annotated[Optional[int], Field(default=None, title="The volume for the issue", description="Enter the Volume of the issue...")]
    issues: Annotated[Optional[int], Field(default=None, title="The issue no. of the volume", description="Enter the issue no. of the volume...")]
    pdfNo: Annotated[Optional[int], Field(default=None, title="The pdf number", description="Enter the pdf number....")]
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
    type :  Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    authors : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    email : Annotated[EmailStr, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    authorsDepartment : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    citation : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    journalYearVolumeIssue : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    content : Annotated[Dict[str, Dict], Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    doi : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    received : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    editorAssigned : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    reviewed : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    revised : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    published : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    manuscriptNo : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
    parentLink : Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")] 
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
def fetchOneP(JournalInputID: str = Path(..., description='Enter your journal input index here....', example="P001",max_length=4)):
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
        async with httpx.AsyncClient(timeout=30.0) as client:  # set timeout explicitly
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
    saveInpData(data)

    # Step 2: Use the topic to search CORE articles
    CORE_API_URL = "https://api.core.ac.uk/v3/search/works"
    headers = {
        "Authorization": f"Bearer {CORE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "q": journal.topic,
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

            core_content_json = build_structured_content(results)

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code,
                            detail=f"CORE API returned HTTP error: {e.response.text}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    # Step 3: Create universal prompt
    prompt = f"""
    You are provided with structured article data extracted from CORE:
    {core_content_json}

    Using this data, 'paraphase it' where that contains only "subContent" and "references" (citation-style reference).

    The final structure should look like:
    "content": {{
      "C001": {{
        "subContent": "...",
        "references": "..."
      }},
      ...
    }}

    Ensure that everything is extracted from the provided article data. 
    Focus on creating references from title, authors, year, and DOI if available, if not then don't replace that with any null or static data, just left it blank.
    And also if possible add some more important ("article" and "journal") data on that topic from your side and merge it with the same thing.
    the most important the whole data will be copied out and used so give me clean information only the structured data no other thing not even a symbol or dot.
    note: Write like a confident, clear thinking human speaking to another smart human.
        Avoid robotic phrases like 'in today's fast-paced world', 'leveraging synergies', or
        'furthermore.
        Skip unnecessary dashes (-), quotation marks (''), and corporate buzzwords like 'cutting-edge', 'robust', or 'seamless experience. No Al tone. No fluff. No filler.
        Use natural transitions like 'here's the thing', ‘let's break it down; or ‘what this really means is’ Keep sentences varied in length and rhythm, like how real people speak or write. Prioritize clarity, personality, and usefulness.
        Every sentence should feel intentional, not generated.
        and also  remove all possible escape sequences like ( \\\\ | \\' | \\" | \\a | \\b | \\f | \\n | \\r | \\t | \\v | \\[0-7]{1,3} | \\x[0-9a-fA-F]{2} | \\u[0-9a-fA-F]{4} | \\U[0-9a-fA-F]{8} ).....
        more specific give a humanized response.
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
    give me a brief summary of between 200 - 400 words from this given data: {core_content_json}

    Summarize the following data. Do not include any introductory labels, brand names, or meta-commentary. Remove all special characters, escape sequences, and formatting symbols. Respond only with plain and clean text containing the summary. Respond without any introductory phrases, labels, brand mentions, or headings (e.g., 'Summary:', 'Gemini:', 'Groq:'). Do not include explanations of how you generated the answer unless explicitly asked.
    and also  remove all possible escape sequences like ( \\\\ | \\' | \\" | \\a | \\b | \\f | \\n | \\r | \\t | \\v | \\[0-7]{1,3} | \\x[0-9a-fA-F]{2} | \\u[0-9a-fA-F]{4} | \\U[0-9a-fA-F]{8} ).....
    more specific give a humanized response.
"""
    try:
        gem_response = gemClient.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        gem_conclusion = gem_response.text
    except Exception as e:
        gem_conclusion = f"Gemini API failed: {str(e)}"


    # Step 8: Title content using Gemini
    prompt = f"give me a 5 to 7 words title based on the generated summary {gem_summary}. use playoff method to generate 5,6 titles and choose the best one and give that title. no need to display background process. just give 1 title as a final response"

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
            "type": journal.type,
            "authors": journal.author,
            "email": "xyz@gmail.com",
            "authorsDepartment": "Department of Biochemistry and Nutrition, Ludwig Maximilian University of Munich, Germany",
            "citation": f"Brown D. How {journal.topic.lower()} shapes personalized nutrition. {journal.generalName}. {journal.published[-4:]};{journal.volume}({journal.issues}):240",
            "journalYearVolumeIssue": f"{journal.generalName} {journal.published} Volume {journal.volume} Issue {journal.issues}",
            "content": content_data,
            "doi": "10.5219/736",
            "received": journal.received,
            "editorAssigned": journal.editorAssigned,
            "reviewed": journal.reviewed,
            "revised": journal.revised,
            "published": journal.published,
            "manuscriptNo": f"AAAFN-{journal.published[-4:]}-{journal.pdfNo}",
            "parentLink": str(journal.parentLink),
            "conclusion": gem_conclusion
        }
    }
    
    data = fetchOutData()
    pulsus_output_instance = PulsusOutputStr(**final_output[journal.id])
    data[journal.id] = pulsus_output_instance.model_dump()
    saveOutData(data)
    return JSONResponse(status_code=200, content="Data Added successfully")

