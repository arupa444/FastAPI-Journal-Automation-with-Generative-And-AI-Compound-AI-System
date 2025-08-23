# 📚 FastAPI Journal Automation with Generative AI (Compound AI System for Journals – Automation API)

A **FastAPI-based** application designed to **automate the creation, enrichment, and management of journal articles**. This system integrates **Large Language Models (LLMs)** such as **Google Gemini (2.5-Flash)** and **Groq’s LLaMA (3.3-70b-versatile)**, combined with the **CORE (Connecting Repositories) API**, to process, enhance, and generate structured journal data, ultimately producing professional **HTML and PDF** documents.

---

## ✨ Key Features

-   **📄 CRUD Operations** – Create, Read, Update, and Delete journal input data.
-   **🤖 Advanced AI-Powered Content Generation** – Utilizes Gemini 2.5-Flash and Groq LLaMA 3.3-70b-versatile to generate, summarize, and structure diverse content (research findings, introductions, descriptions, abstracts, conclusions, and titles).
-   **🔍 Academic Article Search** – Dedicated endpoint to search relevant academic literature via the CORE API. (Note: This is an independent search endpoint, not the primary content source for the automated pipeline).
-   **⚙️ Comprehensive Automated Journal Processing Pipeline** – From initial metadata input to AI-driven content generation, narrative assembly, and final **HTML and LaTeX-based PDF** document output.
-   **✅ Robust Data Validation** – Pydantic-based input and output validation ensuring data integrity and correct formatting, including custom date and uniqueness checks.
-   **📦 Structured JSON Output** – Machine-readable and well-defined journal data for easy integration.
-   **🌐 User Interface (UI)** – Basic web-based interface for interacting with key API functionalities.

---

## 📌 API Endpoints Overview

| Method   | Path                                            | Description                                                                 |
| :------- | :---------------------------------------------- | :-------------------------------------------------------------------------- |
| **GET**  | `/`                                             | Welcome message.                                                            |
| **GET**  | `/about`                                        | Project description.                                                        |
| **GET**  | `/view/journalInputData`                        | Retrieve all journal input data.                                            |
| **GET**  | `/journalInputData/{JournalInputID}`            | Fetch a specific journal input by ID.                                       |
| **POST** | `/addJournalInInput`                            | Add a new journal input.                                                    |
| **PUT**  | `/updateInputJournal/{JournalInputID}`          | Update an existing journal input.                                           |
| **DELETE** | `/delete/journalInputData/{JournalInputID}`     | Delete a journal input by ID.                                               |
| **POST** | `/pulsus-ask-gemini`                            | Send a prompt to the Google Gemini API (model: `gemini-2.5-flash`).       |
| **POST** | `/pulsus-ask-groq`                              | Send a prompt to the Groq API (model: `llama-3.3-70b-versatile`).         |
| **POST** | `/core/search/articles`                         | Search academic articles via CORE API.                                      |
| **POST** | `/pipeline/journal-full-process`                | Execute the full journal processing pipeline to generate HTML & PDF.      |
| **UI**   | `/ui/about`                                     | User interface for project description.                                     |
| **UI**   | `/ui/add-journal`                               | User interface to add new journal input.                                    |
| **UI**   | `/ui/update-journal`                            | User interface to update existing journal input.                            |
| **UI**   | `/ui/ask-gemini`                                | User interface to interact with Gemini.                                     |
| **UI**   | `/ui/ask-groq`                                  | User interface to interact with Groq.                                       |
| **UI**   | `/ui/core-search`                               | User interface to search academic articles using CORE API.                  |
| **UI**   | `/ui/pipeline`                                  | User interface to submit data for the full journal processing pipeline.     |
| **UI**   | `/ui/delete-journal`                            | User interface to delete journal input data.                                |

---

## 🚀 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/arupa444/FastAPI-Journal-Automation-with-Generative-And-AI-Compound-AI-System.git
cd FastAPI-Journal-Automation-with-Generative-And-AI-Compound-AI-System
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

### 4️⃣ Install Software and Font

For successful PDF generation, you need:

1.  **MikTex Software:** Download and Install [MikTex](https://miktex.org/download) to your device. This is essential for compiling LaTeX files into PDFs.
2.  **Archivo Narrow Font:** Download and Install the [Archivo Narrow font](https://fonts.google.com/specimen/Archivo+Narrow) to your device's system fonts. This font is used in the LaTeX templates.

---

## 🔑 Configuration

This application requires API keys for **Google Gemini**, **Groq**, and **CORE**.

1.  Create a `.env` file in the root directory.
2.  Add the following lines with your respective API keys:

    ```env
    gemAPI1="YOUR_GEMINI_API_KEY"
    groqAPI2="YOUR_GROQ_API_KEY"
    coreAPI3="YOUR_CORE_API_KEY"
    ```

---

## ▶️ Usage

### Run the FastAPI Application

```bash
uvicorn main:app --reload
```

### Access Application and API Documentation

Once running, open:

*   **API Documentation (Swagger UI):** `http://127.0.0.1:8000/docs`
*   **API Documentation (Redoc):** `http://127.0.0.1:8000/redoc`
*   **Web User Interface:** `http://127.0.0.1:8000/`

---

## API Endpoint: `POST /pipeline/journal-full-process`

This endpoint represents the core automated pipeline of the application. It accepts detailed information about a journal article, processes it through a multi-step workflow involving Large Language Models (LLMs), and generates fully formatted **HTML** and **PDF** documents as the final output.

### Overview

The pipeline automates the entire process of creating a research article, from initial data input to final document generation. It achieves this by:

1.  **Validating** and storing initial journal metadata.
2.  Using the journal's **topic** to prompt LLMs (Gemini/Groq) to generate structured research content (summaries, references, titles, authors, DOIs, URLs, etc.).
3.  Leveraging further LLM calls to write a **narrative** (introduction, description, abstract, conclusion) and a **suitable title** based on the generated content.
4.  **Assembling** all the original and generated data into a final, coherent structure (`PulsusOutputStr`).
5.  **Generating an HTML file** by injecting the data into a Jinja2 HTML template.
6.  **Generating a PDF file** by injecting this data into a LaTeX template (selected based on `brandName`) and compiling it using `xelatex`.

### 1. Input and Validation

The process begins when a `POST` request is sent to `/pipeline/journal-full-process`. The request body must be a JSON object that conforms to the `PulsusInputStr` Pydantic model.

**Request Body Example (`PulsusInputStr`):**

```json
{
  "id": "J001",
  "topic": "The Impact of AI on Climate Change Prediction Models",
  "journalName": "Journal of Environmental Informatics",
  "shortJournalName": "J Env Inform",
  "type": "Research Article",
  "author": "Dr. Jane Doe",
  "email": "jane.doe@example.com",
  "brandName": "hilaris.tex",
  "authorsDepartment": "Department of Computer Science, University of XYZ, City, Country",
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
  "imgPath": "Logo/logo_sample.png",
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

#### Step 2.1: Structured Content Generation (LLM Prompt #1)

The pipeline uses the `topic` from the input to query the LLMs (Gemini or Groq). This first prompt is designed to generate the core content of the article—a collection of summarized research findings with comprehensive details.

> **Prompt Sent to Gemini/Groq:**
>
> ```
> You are provided by a topic:
> topic : "{journal.topic}"
>
> Using this topic, generate a summarized structure that contains "subContent" (summary of key insights from the article), "references" (citation-style reference) and the remainings and make sure all the journals are authentic not created by you, and i need recent year data's(last 5 years) and must from a legit author and the links must work properly, don't provide any dummy data or dummy link.
>
> The final structure should look like:
> "content": {{
>   "C001": {{
>     "subContent": "...",
>     "references": "...",
>     "title": "...",
>     "authors": "...",
>     "published": "...",
>     "pageRangeOrNumber": "...", #the page range or the page number
>     "volume": "...",
>     "issues": "...",
>     "DOI": "...",
>     "url": "...",
>     "parentLink": "..."
>   }}, # try to achieve the maximum of 10 (C010) counts.
>   ...
> }}
>
> Focus on creating references from title, authors, year, and DOI.
> the most important thing, and the whole data will be copied out and used so give me clean information only the structured data no other thing not even a symbol or dot.
> note: Write like a confident, clear thinking human speaking to another smart human... [and other style instructions]
> ```

**How it's Helpful:** This prompt instructs the LLM to act as a sophisticated research assistant. It finds and structures relevant articles on the given topic into a clean, predictable JSON format, including detailed bibliographic information. This completely automates a significant part of the literature review and summarization process.

#### Step 2.2: Narrative Generation (LLM Prompt #2)

The structured JSON content from the previous step is then used as context for a second LLM call. This prompt's goal is to write the human-readable narrative parts of the article: the introduction, description, summary (conclusion), and abstract.

> **Prompt Sent to Gemini:**
>
> ```
> This is the given data : "{content_data}"
> i want to you to process this data and give me some output:
> 1: Give me a brief summary from the given data where the word count lies in between 200 - 400.
> 2: Give me a brief introduction from the given data where it will contain the citation markers as well, and note, you have to take in this way: the "C001" will be 1, "C002": 2...... and each section should have different but sequencial citation markers (for ex: "C001" will be 1, "C002": 2 and so on). and give two linebreak '\n' after the citation marker and also make sure the citation marker must stays before the full stop '.', and the full introduction word count lies in between 600 - 800.
> 3: Give me a brief description from the given data where it will contain the citation markers as well, and note, you have to take in this way: the "C001" will be 1, "C002": 2...... and each section should have different but sequencial citation markers (for ex: "C001" will be 1, "C002": 2 and so on). and give two linebreak '\n' after the citation marker and also make sure the citation marker must stays before the full stop '.', and the full description word count lies in between 600 - 800.
> 4: Give me a abstract from the given data, and the full abstract word count lies in between 90 - 100.
>
> The final structure should look like:
> "content": {{
>   "introduction": '''...''',
>   "description" : '''...''',
>   "summary" : '''...''',
>   "abstract" : '''...'''
>   ...
> }}
>
> note: Do not include any introductory labels... [and other style/formatting instructions]
> ```

**How it's Helpful:** This step transforms the list of structured summaries into a flowing, academic narrative. It automatically synthesizes the information, adds sequential citation markers (e.g., `[1]`, `[2]`), and adheres to specified word counts, effectively writing the bulk of the article's human-readable content.

#### Step 2.3: Title Generation (LLM Prompt #3)

A final prompt is sent to generate a concise and suitable title for the new article.

> **Prompt Sent to Gemini:**
>
> ```
> give me a 5 to 7 words title based on the generated summary {content_data}. use playoff method to generate 5,6 titles and choose the best one and give that title. no need to display background process. just give 1 title as a final response
> ```

**How it's Helpful:** This automates a creative task, providing a concise and relevant title based on the article's synthesized content, ensuring it's impactful and appropriate.

### 3. Data Assembly and Final Output

The pipeline now gathers all the generated and original data:
*   Original user input (author, dates, DOI, `brandName`, `shortJournalName`, `imgPath`, etc.).
*   The structured content from Step 2.1.
*   The narrative (introduction, description, abstract, summary/conclusion) from Step 2.2.
*   The title from Step 2.3.
*   Several derived fields (like `QCNo`, `preQCNo`, `RManuNo`).
*   A `citation` field which is a Pydantic `computed_field` that dynamically generates a citation string based on the `brandName` and other input data.

This complete dataset is rigorously validated against the `PulsusOutputStr` Pydantic model (which includes validation to remove content items without `subContent` or `references`) and saved to `journalDBOutput.json`.

### 4. HTML Generation

This new step creates a web-friendly version of the generated journal article.

1.  **Templating:** The system uses the **Jinja2** templating engine to load a predefined HTML template (`Format1.html`).
2.  **Rendering:** The assembled JSON data (`PulsusOutputStr`) is passed as context to the template. Jinja2 replaces placeholders in the HTML file with the actual data. This includes dynamically creating clickable citation links (`[<a href='#{i}' title='{i}'>{i}</a>]`) and generating a styled reference list.
3.  **Saving:** The rendered HTML content is saved as a `.html` file, named using the journal ID (e.g., `J001.html`).

### 5. PDF Generation

This is the final step where the digital data becomes a professional, print-ready document.

1.  **Templating:** The system uses the **Jinja2** templating engine to load a LaTeX template. The specific LaTeX template (`hilaris.tex`, `alliedAcademy.tex`, `omics.tex`) is dynamically selected based on the `brandName` field in the input.
2.  **LaTeX Escaping:** A custom `latex_escape` filter is applied to the data to ensure special characters (like `&`, `%`, `_`) are correctly escaped for LaTeX, preventing compilation errors.
3.  **Rendering:** The assembled JSON data is passed as context to the chosen LaTeX template. Jinja2 replaces placeholders (e.g., `\VAR{title}`, `\VAR{introduction}`) with the escaped data.
4.  **Compilation:** The script executes `xelatex` (a powerful TeX engine) on the rendered `.tex` file twice. This ensures all cross-references, citations, and table of contents are correctly resolved. The compiler generates a high-quality PDF document, complete with professional formatting, sections, and references. The output file is named using the journal ID (e.g., `J001.pdf`).

### 6. Successful Response

If all steps complete successfully, the API returns a `200 OK` status with the following JSON response, and new HTML and PDF files will be present on the server.

```json
{
  "Status": "Data added successfully and generated PDF successfully ✅."
}
```

---

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
    "shortJournalName": "J Anim Health Behav Sci",
    "type": "Short Communication",
    "author": "Jhump James",
    "email": "jhumpjames1@gmail.com",
    "brandName": "alliedAcademy.tex",
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
    "imgPath": "Logo/logo_sample.png",
    "parentLink": "https://www.alliedacademies.org/archives-food-nutrition/"
}
```

---

## 📄 License

**Open for everyone** – Free to use and modify. As this is free and made for you all, please consider leaving a star on my repo!

---

## 📬 Contact

For queries or contributions:

*   **Author:** Arupa Nanda Swain
*   **GitHub:** https://github.com/arupa444
*   **Email:** arupaswain7735@gmail.com
