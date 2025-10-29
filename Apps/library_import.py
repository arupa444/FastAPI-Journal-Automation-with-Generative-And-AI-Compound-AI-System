"""
imports.py
Centralized import module for the project.
This file consolidates all necessary third-party and standard library imports
for consistent access across different modules.
"""

# ==========================
# 🧩 Standard Library Imports
# ==========================
import os
import re
import time
import json
import uuid
import copy
import httpx
import datetime
import asyncio
import subprocess
from math import e
from pathlib import Path

pathOfPathLib = Path

# ==========================
# 🧱 Third-Party Libraries
# ==========================
from fastapi import FastAPI, Path, HTTPException, Query, Request, Form, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel, Field, field_validator, computed_field, AnyUrl, EmailStr

from typing import Annotated, Literal, Optional, List, Dict, Any

from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# ==========================
# 🤖 AI / API SDK Imports
# ==========================
from google import genai
from groq import Groq

# ==========================
# 🌍 Translation
# ==========================
# from googletrans import Translator  # Optional alternative
from deep_translator import GoogleTranslator

# ==========================
# 🧾 Module Metadata
# ==========================
__all__ = [
    # Core
    "os",
    "re",
    "time",
    "json",
    "uuid",
    "copy",
    "httpx",
    "datetime",
    "asyncio",
    "subprocess",
    "pathOfPathLib",
    "e",
    # FastAPI
    "FastAPI",
    "Path",
    "HTTPException",
    "Query",
    "Request",
    "Form",
    "JSONResponse",
    "HTMLResponse",
    "Jinja2Templates",
    "StaticFiles",
    # Pydantic
    "BaseModel",
    "Field",
    "field_validator",
    "computed_field",
    "AnyUrl",
    "EmailStr",
    # Typing
    "Annotated",
    "Literal",
    "Optional",
    "List",
    "Dict",
    "Any",
    # Jinja / Env
    "Environment",
    "FileSystemLoader",
    "load_dotenv",
    # AI SDKs
    "genai",
    "Groq",
    # Translation
    "GoogleTranslator",
]
