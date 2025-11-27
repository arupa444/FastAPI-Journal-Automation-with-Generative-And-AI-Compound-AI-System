# pdfGen1.4 – Installation & Usage Guide (Windows)

pdfGen1.4 is a locally hosted PDF generation tool built using **Python**, **FastAPI**, and **MiKTeX** for LaTeX-based rendering.  
Due to hosting and API credit limitations, the project is designed to run entirely on your local machine while allowing free usage of Gemini APIs through local execution.

---

## 🖥️ System Requirements

- **Operating System:** Windows 11  
- **Python Version:** **3.12.8**  
- **LaTeX Distribution:** MiKTeX 24.1+  
- **Virtual Environment:** Recommended (`.venv`, `.conda`, `uv`, etc.)

---

## 🐍 Step 1 — Install Python 3.12.8

Download the official Python installer:

🔗 https://www.python.org/ftp/python/3.12.8/python-3.12.8-amd64.exe

### During installation:
1. Click **Customize Installation**  
2. Enable **Add python.exe to PATH**  
3. Proceed with recommended settings  
4. Complete installation

### Verify installation

Open **PowerShell** or **CMD**:

```bash
python --version
pip --version
```

Expected:

```
Python 3.12.8
pip <version>
```

---

## 📦 Step 2 — Install MiKTeX

Download MiKTeX:

🔗 https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-24.1-x64.exe

### After installation:
- Open **MiKTeX Console**
- Enable: **Install missing packages on-the-fly**
- Click **Updates** → **Update All**

This ensures LaTeX packages required for PDF rendering are available.

---

## 📁 Step 3 — Set Up Virtual Environment

Inside your project directory:

```bash
python -m venv .venv
```

### Activate the environment:

**PowerShell**
```bash
.\.venv\Scripts\Activate
```

**CMD**
```bash
.\.venv\Scriptsctivate.bat
```

---

## 📚 Step 4 — Install Dependencies

Once your virtual environment is active:

```bash
pip install -r requirements.txt
```

This installs FastAPI, Uvicorn, LaTeX-related utilities, and other required packages.

---

## 🚀 Step 5 — Run the Application

You can start the server in two ways:

### **Option A — Using Uvicorn**

```bash
uvicorn app:app --reload
```

Open the displayed **localhost** link (e.g., http://127.0.0.1:8000).

### **Option B — Using runServer.bat**

Just double‑click:

```
runServer.bat
```

It will automatically start the backend and open the web interface.

---

## ℹ️ Why Local Installation?

Because:
- Hosting requires paid servers  
- Gemini API has limited credits  
- Local installation allows using free API keys from multiple accounts  
- All heavy processing happens on your device without cloud limits  

This ensures full flexibility and zero hosting cost.

---

## 📄 License

This project is currently intended for internal or private usage.  
Modify as needed based on your licensing preferences.
