# 📚 Compound AI System for Journals – Automation API

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

```json output str of journalDBOutput.json
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
```

📌 This triggers:

1. Retrieval of related articles from CORE.
2. AI content generation with Gemini and Groq.
3. Structured JSON output saved in `journalDBOutput.json`.

---

## 📄 License

**Open for everyone** – Free to use and modify. and as this is free made for you all. So don't forget to live a star on my repo.

---

## 📬 Contact

For queries or contributions:

* **Author:** Arupa Nanda Swain
* **GitHub:** https://github.com/arupa444
* **Email:** arupaswain7735@gmail.com
