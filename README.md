# pdfGen — Local LaTeX PDF Generator for Journals ✅

A lightweight, locally-hosted tool that converts journal templates into publication-ready PDFs using FastAPI and LaTeX. Designed to run offline on Windows and optionally integrate with AI services (Gemini, Groq) for assisted content generation and translation — enabling reproducible PDF generation without hosting costs.

---

## Table of Contents

- [About](#pdfgen---local-latex-pdf-generator-for-journals-)
- [Features](#features)
- [Quickstart](#quickstart)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [Contributing](#contributing)
- [License](#license)
- [Contact & Support](#contact--support)

---

## ✨ Features

- Render journal templates (LaTeX) into PDF locally using MiKTeX
- Web interface and API endpoints via FastAPI and Uvicorn
- Optional AI-enhanced content generation (Gemini, Groq)
- Translation support (deep-translator) and multi-language templates
- Local-first workflow — no paid hosting required

---

## 🚀 Quickstart

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repo-root>
   ```
2. Follow the Installation steps below (Windows-specific steps included).
3. Start the app:

   - Option A (recommended):

     ```bash
     python run.py
     ```

     The script finds a free port (8000–8100), launches Uvicorn, and opens your browser.

   - Option B: Run Uvicorn directly:
     ```bash
     uvicorn Apps.app:app --reload --port 8000
     ```

4. Open the URL displayed in the console (e.g., http://127.0.0.1:8000).

---

## 🛠 Installation (Detailed)

**Prerequisites (Windows)**

- Windows 10/11 (latest updates recommended)
- Python 3.12.x (3.12.8 recommended)
- MiKTeX 24.1+ (for LaTeX to PDF rendering)
- Optional: API keys for Google Gemini / Groq / CORE if you plan to use AI or search features

**Detailed steps**

1. Verify Python is installed and accessible

   ```powershell
   python --version
   pip --version
   python -m pip install --upgrade pip
   ```

   If `python` is not found, reinstall Python and ensure you enable **Add python.exe to PATH**.

2. Install MiKTeX

   - Download MiKTeX: https://miktex.org/download
   - Run the MiKTeX installer and open MiKTeX Console afterwards.
   - In MiKTeX Console: enable **Install missing packages on-the-fly** and run **Update**.
   - If `xelatex` is not on PATH after install, add MiKTeX's `miktex/bin` folder to your PATH or use the MiKTeX Console to fix PATH settings.

3. Create & activate a virtual environment (recommended)
   PowerShell (recommended):

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   ```

   CMD:

   ```cmd
   python -m venv .venv
   .\.venv\Scripts\activate.bat
   ```

4. Install Python dependencies

   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables (optional for AI features)
   Create a `.env` file in the project root or set system environment variables. Example `.env`:

   ```env
   gemAPI1=your_gemini_api_key_here
   groqAPI2=your_groq_api_key_here
   coreAPI3=your_core_api_key_here
   ```

   Note: `Apps/config.py` loads these variables as `gemAPI1`, `groqAPI2`, and `coreAPI3`.

6. (Optional) Run a quick LaTeX test
   Create a file `temp/test.tex` with a minimal document and run `xelatex` manually or via the app to ensure MiKTeX is working:
   ```tex
   \documentclass{article}
   \begin{document}
   Hello, pdfGen!
   \end{document}
   ```
   Then
   ```powershell
   xelatex -interaction=nonstopmode -output-directory=temp temp/test.tex
   ```
   If this succeeds, `temp/test.pdf` should be created.

---

## ▶️ Usage (Detailed)

### Start the server

- Recommended (auto-port + browser opener):

  ```bash
  python run.py
  ```

  This script auto-selects an available port in the range 8000–8100, starts Uvicorn and opens your browser.

- Or start Uvicorn manually (use this if you want a fixed port):

  ```bash
  uvicorn Apps.app:app --reload --port 8000
  ```

- Windows quick launcher:
  - Double-click `runServer.bat` to run `run.py` using the default Python on your PATH.

### Web UI

- After the server starts, open the printed URL (e.g., http://127.0.0.1:8000).
- Useful UI pages:
  - `GET /ui/add-journal` — Add a new journal entry via the web form
  - `GET /ui/update-journal` — Edit an existing journal
  - `GET /ui/ask-gemini` — Gemini prompt UI
  - `GET /ui/ask-groq` — Groq prompt UI
  - `GET /ui/pipeline` — Pipeline controls
  - `GET /ui/translate` — Translate page UI

### Key API Endpoints (examples)

- Compile LaTeX to PDF (endpoint used by UI):

  ```http
  POST /compile-latex
  Content-Type: application/json

  { "source": "\\documentclass{article}\\begin{document}Hello\\end{document}" }
  ```

  Response on success:

  ```json
  { "pdf_path": "/static/<job_id>.pdf" }
  ```

  You can then open `http://127.0.0.1:<port>/static/<job_id>.pdf` to download the PDF.

- Full pipeline (journal -> PDF):

  ```http
  POST /pipeline/journal-full-process
  Content-Type: application/json

  {
    "id": "a123",
    "topic": "Example Topic",
    "journalName": "Example Journal",
    "shortJournalName": "EJ",
    "type": "Research Article",
    "author": "Jane Doe",
    "email": "jane@example.com",
    "brandName": "alliedAcademy.tex",
    "authorsDepartment": "CS",
    "received": "2025-12-01",
    "manuscriptNo": "M-001",
    "volume": 1,
    "issues": 1,
    "pdfNo": 1,
    "parentLink": "https://example.org/journal"
  }
  ```

  This triggers the full processing pipeline and returns the generated output or status.

- Translate generated journal page to another language:

  ```http
  POST /pdfs/translate
  Content-Type: application/json

  { "id": "a123", "language": "Spanish" }
  ```

- LLM endpoints (Gemini / Groq / CORE search):
  ```http
  POST /llm/ask-gemini    { "prompt": "Write an abstract about X" }
  POST /llm/ask-groq      { "prompt": "Summarize this introduction" }
  POST /llm/core/search   { "prompt": "Search query for core" }
  ```

### Storage paths

- Generated outputs: `Apps/DB/PDFStorePulsus/` (`<journal_id>/` subfolders)
- Temporary LaTeX artifacts & logs: `Apps/DB/TempLogsPulsus/` and `temp/`

---

## 🔧 Troubleshooting & Tips

- Port already in use: specify `--port` when using Uvicorn or inspect running services and stop the conflicting process.
- `xelatex` command not found: ensure MiKTeX is installed and the binary folder is on your PATH.
- LaTeX missing packages: enable on-the-fly installation in MiKTeX Console and re-run the compile step; then update MiKTeX packages.
- If AI endpoints return errors: verify API keys are set (`gemAPI1`, `groqAPI2`, `coreAPI3`) in a `.env` or environment variables.

---

## 👤 Author & Contact

**Author:** John Doe  
**Email:** john.doe@example.com  
**Repository:** https://github.com/johndoe/pdfGen

_These are placeholder contact values. Replace them with real author name, email, and repository URL when you're ready._

Please replace the placeholders above with actual contact details. To report bugs or request features, open an issue on GitHub.

---

## 📜 License

MIT License

Copyright (c) 2025 John Doe

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🆘 Contact & Support

- Report issues: open an issue on GitHub (preferred)
- For questions or collaboration: email the project author (see Author & Contact above)
- For local installation issues: check `installationGuild.md` for step-by-step Windows setup

> 🔧 Tip: When submitting an issue, include steps to reproduce, console logs, and any LaTeX error output you see in the server logs.

---

If you'd like, I can replace the contact placeholders with your real name/email and add a GitHub Actions workflow for basic CI (linting/tests).
