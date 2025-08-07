# 📚FastAPI Journal Automation with Generative AI(Compound AI System for Journals – Automation API)

A **FastAPI-based** application designed to **automate the creation, enrichment, and management of journal articles**.  
This system integrates **Large Language Models (LLMs)** such as **Google Gemini** and **Groq’s LLaMA**, combined with the **CORE (Connecting Repositories) API**, to process and enhance journal data.

---

## ✨ Key Features

- **📄 CRUD Operations** – Create, Read, Update, and Delete journal input data.
- **🤖 AI-Powered Content Generation** – Use Gemini and Groq to generate and summarize content.
- **🔍 Academic Article Search** – Search relevant academic literature via the CORE API.
- **⚙️ Automated Journal Processing Pipeline** – From metadata input to final structured output.
- **✅ Data Validation** – Pydantic-based robust input and output validation.
- **📦 Structured JSON Output** – Easy-to-integrate, machine-readable journal data.

---

## 📌 API Endpoints Overview

| Method | Path                                        | Description |
|--------|---------------------------------------------|-------------|
| **GET** | `/`                                         | Welcome message. |
| **GET** | `/about`                                    | Project description. |
| **GET** | `/view/journalInputData`                    | Retrieve all journal input data. |
| **GET** | `/journalInputData/{JournalInputID}`        | Fetch a specific journal input by ID. |
| **POST** | `/addJournalInInput`                       | Add a new journal input. |
| **PUT** | `/updateInputJournal/{JournalInputID}`      | Update an existing journal input. |
| **DELETE** | `/delete/journalInputData/{JournalInputID}` | Delete a journal input by ID. |
| **POST** | `/pulsus-ask-gemini`                       | Send a prompt to the Gemini API. |
| **POST** | `/pulsus-ask-groq`                         | Send a prompt to the Groq API. |
| **POST** | `/core/search/articles`                    | Search academic articles via CORE API. |
| **POST** | `/pipeline/journal-full-process`           | Execute the full journal processing pipeline. |

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone <your-repository-url>
cd <your-repository-directory>
```


### 2️⃣ Create & Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
## 🔑 Configuration

This application requires API keys for **Gemini**, **Groq**, and **CORE**.

1. Create a `.env` file in the root directory.  
2. Add the following lines with your respective API keys:  

```env
gemAPI1="YOUR_GEMINI_API_KEY"
groqAPI2="YOUR_GROQ_API_KEY"
coreAPI3="YOUR_CORE_API_KEY"
```
## ▶️ Usage
### Run the FastAPI Application
```bash
uvicorn main:app --reload
```
### Access API Documentation

Once running, open:

```
http://127.0.0.1:8000/docs
```

or

```
http://127.0.0.1:8000/redoc
```

---


## API Endpoint: `POST /pipeline/journal-full-process`

This endpoint represents the core automated pipeline of the application. It accepts detailed information about a journal article, processes it through a multi-step workflow involving Large Language Models (LLMs), and generates a fully formatted PDF document as the final output.

### Overview

The pipeline automates the entire process of creating a research article summary, from initial data input to final document generation. It achieves this by:

1.  **Validating** and storing initial journal metadata.
2.  Using the journal's **topic** to prompt LLMs (Gemini and Groq) to research and generate structured content.
3.  Leveraging further LLM calls to write a **narrative** (introduction, description, conclusion) and a **title** based on the generated content.
4.  **Assembling** all the original and generated data into a final, coherent structure.
5.  **Injecting** this data into a LaTeX template.
6.  **Compiling** the LaTeX file into a professional-grade PDF.

### 1. Input and Validation

The process begins when a `POST` request is sent to `/pipeline/journal-full-process`. The request body must be a JSON object that conforms to the `PulsusInputStr` Pydantic model.

**Request Body Example (`PulsusInputStr`):**

```json
{
  "id": "J001",
  "topic": "The Impact of AI on Climate Change Prediction Models",
  "journalName": "Journal of Environmental Informatics",
  "type": "Research Article",
  "citation": "Author A. (2025). Title. Journal of Environmental Informatics, 10(2), 123.",
  "author": "Dr. Jane Doe",
  "email": "jane.doe@example.com",
  "authorsDepartment": "Department of Computer Science",
  "received": "01-Jan-2025",
  "editorAssigned": "15-Jan-2025",
  "reviewed": "01-Feb-2025",
  "revised": "15-Feb-2025",
  "published": "01-Mar-2025",
  "manuscriptNo": "JEI-2025-001",
  "volume": 10,
  "issues": 2,
  "pdfNo": 123,
  "doi": "10.1234/jei.2025.001",
  "ISSN": "1234-5678",
  "parentLink": "https://example.com/journal"
}
```

**Validation Process:**

Before any processing occurs, the input data is rigorously validated by Pydantic:

*   **Type Checking:** Ensures fields like `volume` and `pdfNo` are integers and `email` is a valid email format.
*   **Custom Date Validation:** The `validateDates` validator checks that all date fields (`received`, `published`, etc.) are in the correct `DD-Mmm-YYYY` format (e.g., `01-Mar-2025`).
*   **Uniqueness Check:** The `validatePDFNo` validator checks against the `journalDBInput.json` file to ensure the `pdfNo` has not been used before, preventing duplicate entries.
*   **ID Check:** The endpoint logic itself checks if the provided `id` already exists in the database, raising an error if it does to prevent overwriting existing data.

### 2. The Automated Workflow

If the input is valid, the main pipeline begins.

#### Step 2.1: Content Generation (LLM Prompt #1)

The pipeline uses the `topic` from the input to query the LLMs. This first prompt is designed to generate the core content of the article—a collection of summarized research findings with proper references.

> **Prompt Sent to Gemini/Groq:**
>
> ```
> You are provided by a topic:
> topic : "{journal.topic}"
>
> Using this data, generate a summarized structure that contains only "subContent" (summary of key insights from the article) and "references" (citation-style reference).
>
> The final structure should look like:
> "content": {{
>   "C001": {{
>     "subContent": "...",
>     "references": "...",
>     "parentLink": "..." #parent link is the link where we can find the article or the journal
>   }}, # try to achieve as much as possible but maximum will be 15(C015) and the minimum will be 10(C010)
>   ...
> }}
>
> Ensure the summaries are meaningful and extracted from the provided article data.
> Focus on creating references from title, authors, year, and DOI if available.
> And also if possible add some more important ("article" and "journal") data on that topic from your side and merge it with the same thing.
> the most important the whole data will be copied out and used so give me clean information only the structured data no other thing not even a symbol or dot.
> note: Write like a confident, clear thinking human... [and other style instructions]
> ```

**How it's Helpful:** This prompt instructs the LLM to act as a research assistant. It searches its vast knowledge base for relevant articles on the given topic and structures the findings into a clean, predictable JSON format. This completely automates the literature review and summarization process.

#### Step 2.2: Narrative Generation (LLM Prompt #2)

The structured JSON content from the previous step is then used as context for a second LLM call. This prompt's goal is to write the human-readable parts of the article: the introduction, description, and conclusion.

> **Prompt Sent to Gemini:**
>
> ```
> This is the given data : "{content_data}"
> i want to you to process this data and give me some output:
> 1: Give me a brief summary from the given data where the word count lies in between 200 - 400.
> 2: Give me a brief introduction from the given data where it will contain the citation markers as well, and you have to take in this way: the "C001" will be 1, "C002": 2......, where the word count lies in between 600 - 800.
> 3: Give me a brief description from the given data where it will contain the citation markers as well, and you have to take in this way: the "C001" will be 1, "C002": 2......, where the word count lies in between 600 - 800.
>
> The final structure should look like:
> "content": {{
>   "introduction": '''...''',
>   "description" : '''...''',
>   "summary" : '''...'''
>   ...
> }}
>
> note: Do not include any introductory labels... [and other style/formatting instructions]
> ```

**How it's Helpful:** This step transforms the list of discrete summaries into a flowing narrative. It automatically synthesizes the information, adds citation markers (e.g., `[1]`, `[2]`), and adheres to specified word counts, effectively writing the bulk of the article.

#### Step 2.3: Title Generation (LLM Prompt #3)

A final, simple prompt is sent to generate a suitable title for the new article.

> **Prompt Sent to Gemini:**
>
> ```
> give me a 5 to 7 words title based on the generated summary {content_data}. use playoff method to generate 5,6 titles and choose the best one and give that title. no need to display background process. just give 1 title as a final response
> ```

**How it's Helpful:** This automates a creative task, providing a concise and relevant title based on the article's synthesized content.

### 3. Data Assembly and Final Output

The pipeline now gathers all the pieces:
*   Original user input (author, dates, DOI, etc.).
*   The structured content from Step 2.1.
*   The narrative (introduction, description, summary) from Step 2.2.
*   The title from Step 2.3.
*   Several derived fields (like `QCNo`, `RManuNo`).

This complete dataset is validated against the `PulsusOutputStr` model and saved to `journalDBOutput.json`.

### 4. PDF Generation

This is the final step where the digital data becomes a physical document.

1.  **Templating:** The system uses the **Jinja2** templating engine to load a LaTeX template (`finalFormate.tex`).
2.  **Rendering:** The assembled JSON data is passed as context to the template. Jinja2 replaces placeholders in the `.tex` file (e.g., `\VAR{title}`, `\VAR{introduction}`) with the actual data.
3.  **Compilation:** The script executes a command-line process (`pdflatex`) on the rendered `.tex` file. This powerful typesetter compiles the LaTeX code into a high-quality PDF document, complete with proper formatting, sections, and references. The output file is named using the journal ID (e.g., `J001.pdf`).

### 5. Successful Response

If all steps complete successfully, the API returns a `200 OK` status with the following JSON response, and a new PDF file will be present on the server.

```json
{
  "message": "Data Added successfull and generated PDF successfully✅."
}
```


## 🛠 Example: Full Journal Automation Workflow

Send a `POST` request to:

```
/pipeline/journal-full-process
```

with JSON body:

```json
{
    "id": "L003",
    "topic": "Vocal Communication Patterns in Bottlenose Dolphins",
    "journalName": "Journal of Animal Health and Behavioural Science",
    "type": "Short Communication",
    "citation": " James, Jhump. “Understanding Vocal Communication Patterns in Bottlenose Dolphins.” J Anim Health Behav Sci 8 (2024): 252.",
    "author": "Jhump James",
    "email": "jhumpjames1@gmail.com",
    "authorsDepartment": "Department of Psychiatry, The University of Mostaganem, Algeria, Africa",
    "received": "01-Apr-2024",
    "editorAssigned": "03-Dec-2024",
    "reviewed": "24-Dec-2024",
    "revised": "24-Dec-2024",
    "published": "31-Dec-2024",
    "manuscriptNo": "ahbs-24-140508",
    "volume": 8,
    "issues": 2,
    "pdfNo": 444,
    "doi": "10.37421/2952-8097.2024.8.252",
    "ISSN": "2952-8097",
    "parentLink": "https://www.alliedacademies.org/archives-food-nutrition/"
}
```

{
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


## 📄 License

**Open for everyone** – Free to use and modify. and as this is free made for you all. So don't forget to live a star on my repo.

---

## 📬 Contact

For queries or contributions:

* **Author:** Arupa Nanda Swain
* **GitHub:** https://github.com/arupa444
* **Email:** arupaswain7735@gmail.com
