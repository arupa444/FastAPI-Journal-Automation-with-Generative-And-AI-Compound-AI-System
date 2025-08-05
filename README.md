# Journal Automation API

This project is a FastAPI-based application designed to automate the process of creating and managing journal articles. It leverages the power of Large Language Models (LLMs) like Google's Gemini and Groq's LLaMA, along with the CORE (Connecting Repositories) API, to enrich and process journal data.

## Features

*   **CRUD Operations for Journal Input**: Create, Read, Update, and Delete journal input data.
*   **AI-Powered Content Generation**: Utilizes Gemini and Groq to generate and summarize content.
*   **Academic Article Search**: Integrates with the CORE API to search for relevant academic articles.
*   **Automated Journal Processing Pipeline**: A complete pipeline that takes journal metadata, fetches related articles, generates content, and structures it into a final journal output.
*   **Data Validation**: Employs Pydantic for robust data validation of inputs and outputs.
*   **Structured JSON Output**: Generates well-formed JSON responses for easy integration with other services.

## API Endpoints

Here is a summary of the available API endpoints:

| Method | Path                                      | Description                                                                 |
| :----- | :---------------------------------------- | :-------------------------------------------------------------------------- |
| GET    | `/`                                       | Home endpoint with a welcome message.                                       |
| GET    | `/about`                                  | Provides a brief description of the project.                                |
| GET    | `/view/journalInputData`                  | Retrieves all journal input data from the database.                         |
| GET    | `/journalInputData/{JournalInputID}`      | Fetches a specific journal input by its ID.                                 |
| POST   | `/addJournalInInput`                      | Adds a new journal to the input database.                                   |
| PUT    | `/updateInputJournal/{JournalInputID}`    | Updates an existing journal's input data.                                   |
| DELETE | `/delete/journalInputData/{JournalInputID}` | Deletes a journal input from the database.                                  |
| POST   | `/pulsus-ask-gemini`                      | Sends a prompt to the Gemini API for processing.                            |
| POST   | `/pulsus-ask-groq`                        | Sends a prompt to the Groq API for processing.                              |
| POST   | `/core/search/articles`                   | Searches for academic articles using the CORE API based on a prompt.        |
| POST   | `/pipeline/journal-full-process`          | Executes the full journal processing pipeline for a given journal input.    |

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <your-repository-directory>
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(You will need to create a `requirements.txt` file based on the imports in your script).*

## Configuration

This application requires API keys for Gemini, Groq, and the CORE API.

1.  Create a `.env` file in the root directory of the project.

2.  Add the following environment variables to your `.env` file with your respective API keys:

    ```
    gemAPI1="YOUR_GEMINI_API_KEY"
    groqAPI2="YOUR_GROQ_API_KEY"
    coreAPI3="YOUR_CORE_API_KEY"
    ```

## Usage

1.  **Run the FastAPI application:**
    ```bash
    uvicorn main:app --reload
    ```
    *(Assuming your Python file is named `main.py`)*

2.  **Access the API documentation:**
    Once the server is running, you can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

### Example Workflow: Full Journal Pipeline

To run the complete journal automation process, send a `POST` request to the `/pipeline/journal-full-process` endpoint with the following JSON payload:

```json
{
  "id": "P001",
  "topic": "Nutrigenomics",
  "type": "Research Article",
  "author": "Dr. Jane Doe",
  "received": "01-Jan-2024",
  "editorAssigned": "05-Jan-2024",
  "reviewed": "15-Jan-2024",
  "revised": "25-Jan-2024",
  "published": "10-Feb-2024",
  "generalName": "Journal of Nutritional Science",
  "keyword": ["genetics", "nutrition", "personalized medicine"],
  "volume": 12,
  "issues": 2,
  "pdfNo": 101,
  "parentLink": "http://example.com/journal"
}
```
This will trigger the entire pipeline, resulting in a new, structured journal entry being saved to journalDBOutput.json.
### Lisencing
Open to use. for every one
