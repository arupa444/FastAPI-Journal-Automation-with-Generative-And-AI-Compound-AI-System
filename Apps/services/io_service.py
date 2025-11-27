from Apps.library_import import json, Dict, Any, re
from Apps.library_import import pathOfPathLib


class IOService:
    """Service class for handling I/O operations of journal data."""

    # ==========================
    # 🧩 Input Data Handling
    # ==========================
    DB_DIR = pathOfPathLib(__file__).resolve().parent.parent / "DB"
    DB_DIR.mkdir(parents=True, exist_ok=True)

    INPUT_FILE = DB_DIR / "journalDBInput.json"
    OUTPUT_FILE = DB_DIR / "journalDBOutput.json"

    @staticmethod
    def fetchInputData() -> Dict[str, Any]:
        """
        Fetch input journal data from `journalDBInput.json`.
        Returns an empty dict if the file is missing or invalid.
        """
        if not IOService.INPUT_FILE.exists():
            return {}

        try:
            with open(IOService.INPUT_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    @staticmethod
    def saveInputData(data: Dict[str, Any]) -> None:
        """
        Save input journal data to `journalDBInput.json`.
        Overwrites the file each time.
        """
        data = data or {}
        with open(IOService.INPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False, default=str)

    # ==========================
    # 📤 Output Data Handling
    # ==========================

    @staticmethod
    def fetchOutputData() -> Dict[str, Any]:
        """
        Fetch output journal data from `journalDBOutput.json`.
        Returns an empty dict if the file is missing or invalid.
        """
        if not IOService.OUTPUT_FILE.exists():
            return {}

        try:
            with open(IOService.OUTPUT_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    @staticmethod
    def saveOutputData(data: Dict[str, Any]) -> None:
        """
        Save output journal data to `journalDBOutput.json`.
        Overwrites the file each time.
        """
        data = data or {}
        with open(IOService.OUTPUT_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False, default=str)

    # ==========================
    # 🧠 Text Utilities
    # ==========================

    @staticmethod
    def extract_json_from_markdown(text: str) -> str:
        """
        Extract JSON content from markdown-style fenced code blocks.

        Example:
        ```json
        {"key": "value"}
        ```
        """
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        return match.group(1) if match else text.strip()
