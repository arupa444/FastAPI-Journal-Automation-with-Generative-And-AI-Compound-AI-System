from math import e
from fastapi import FastAPI, Path, HTTPException, Query, Request, Form
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
import json, time, datetime, httpx, copy, re
from pydantic import BaseModel, Field, field_validator, computed_field, AnyUrl, EmailStr
from typing import Annotated, Literal, Optional, List, Dict
import subprocess, uuid, os
from pathlib import Path as pathOfPathLib
from jinja2 import Environment, FileSystemLoader
from google import genai
from groq import Groq
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# to translate
import asyncio
# from googletrans import Translator
from deep_translator import GoogleTranslator

brand_fonts = {
    "default": r"""
    \usepackage{fontspec}
    \setmainfont{Times New Roman}[
        Path=../../Fonts/,
        UprightFont    = * ,
        BoldFont       = *-Bold ,
        ItalicFont     = *-Italic ,
        BoldItalicFont = *-BoldItalic
    ]""",
        
    "alliedAcademy": r"""
    \usepackage{fontspec}
    \setmainfont{Times New Roman}[
        Path=../../Fonts/,
        UprightFont    = * ,
        BoldFont       = *-Bold ,
        ItalicFont     = *-Italic ,
        BoldItalicFont = *-BoldItalic
    ]""",
    
    "hilaris": r"""
    \usepackage{fontspec}
    \setmainfont{ArchivoNarrow}[
        Path=../../Fonts/,
        UprightFont    = *-Regular ,
        BoldFont       = *-Bold ,
        ItalicFont     = *-Italic ,
        BoldItalicFont = *-BoldItalic
    ]""",

    "iomc": r"""
    \usepackage{fontspec}
    \setmainfont{Times New Roman}[
        Path=../../Fonts/,
        UprightFont    = * ,
        BoldFont       = *-Bold ,
        ItalicFont     = *-Italic ,
        BoldItalicFont = *-BoldItalic
    ]""",

    "bromicsandC": r"""
    \usepackage{fontspec}
    \setmainfont{Times New Roman}[
        Path=../../Fonts/,
        UprightFont    = * ,
        BoldFont       = *-Bold ,
        ItalicFont     = *-Italic ,
        BoldItalicFont = *-BoldItalic
    ]"""
}

def get_lang_map(brand="default"):
    lang_map = {
        "default": {
            "polyglossia": r"\setdefaultlanguage{english}",
            "font": brand_fonts.get(brand, brand_fonts["default"])
        },
        # === Indic Scripts (Devanagari, Tamil, Bengali, etc.) ===
        "hi": {"polyglossia": r"\setdefaultlanguage{hindi}", "font": r"\newfontfamily\hindifont{NotoSansDevanagari-Regular.ttf}[Path=../../Fonts/, Script=Devanagari]"},
        "mr": {"polyglossia": r"\setdefaultlanguage{marathi}", "font": r"\newfontfamily\marathifont{NotoSansDevanagari-Regular.ttf}[Path=../../Fonts/, Script=Devanagari]"},
        "bn": {"polyglossia": r"\setdefaultlanguage{bengali}", "font": r"\newfontfamily\bengalifont{NotoSansBengali-Regular.ttf}[Path=../../Fonts/, Script=Bengali]"},
        "gu": {"polyglossia": r"\setdefaultlanguage{gujarati}", "font": r"\newfontfamily\gujaratifont{NotoSansGujarati-Regular.ttf}[Path=../../Fonts/, Script=Gujarati]"},
        "kn": {"polyglossia": r"\setdefaultlanguage{kannada}", "font": r"\newfontfamily\kannadafont{NotoSansKannada-Regular.ttf}[Path=../../Fonts/, Script=Kannada]"},
        "ta": {"polyglossia": r"\setdefaultlanguage{tamil}", "font": r"\newfontfamily\tamilfont{NotoSansTamil-Regular.ttf}[Path=../../Fonts/, Script=Tamil]"},
        "te": {"polyglossia": r"\setdefaultlanguage{telugu}", "font": r"\newfontfamily\telugufont{NotoSansTelugu-Regular.ttf}[Path=../../Fonts/, Script=Telugu]"},
        "ml": {"polyglossia": r"\setdefaultlanguage{malayalam}", "font": r"\newfontfamily\malayalamfont{NotoSansMalayalam-Regular.ttf}[Path=../../Fonts/, Script=Malayalam]"},
        "or": {"polyglossia": r"\setdefaultlanguage{odia}", "font": r"\newfontfamily\odiafont{NotoSansOriya-Regular.ttf}[Path=../../Fonts/, Script=Oriya]"},
        "pa": {"polyglossia": r"\setdefaultlanguage{punjabi}", "font": r"\newfontfamily\punjabifont{NotoSansGurmukhi-Regular.ttf}[Path=../../Fonts/, Script=Gurmukhi]"},
        "ne": {"polyglossia": r"\setdefaultlanguage{nepali}", "font": r"\newfontfamily\nepalifont{NotoSansDevanagari-Regular.ttf}[Path=../../Fonts/, Script=Devanagari]"},
        "as": {"polyglossia": r"\setdefaultlanguage{assamese}", "font": r"\newfontfamily\assamesefont{NotoSansBengali-Regular.ttf}[Path=../../Fonts/, Script=Bengali]"},
        "mai": {"polyglossia": r"\setdefaultlanguage{maithili}", "font": r"\newfontfamily\maithilifont{NotoSansDevanagari-Regular.ttf}[Path=../../Fonts/, Script=Devanagari]"},
        "bho": {"polyglossia": r"\setdefaultlanguage{bhojpuri}", "font": r"\newfontfamily\bhojpurifont{NotoSansDevanagari-Regular.ttf}[Path=../../Fonts/, Script=Devanagari]"},
        "gom": {"polyglossia": r"\setdefaultlanguage{konkani}", "font": r"\newfontfamily\konkanifont{NotoSansDevanagari-Regular.ttf}[Path=../../Fonts/, Script=Devanagari]"},
        "sa": {"polyglossia": r"\setdefaultlanguage{sanskrit}", "font": r"\newfontfamily\sanskritfont{NotoSansDevanagari-Regular.ttf}[Path=../../Fonts/, Script=Devanagari]"},
        "mni-Mtei": {"polyglossia": r"\setdefaultlanguage{manipuri}", "font": r"\newfontfamily\manipurifont{NotoSansMeeteiMayek-Regular.ttf}[Path=../../Fonts/]"},

        # === Arabic Script (Urdu, Persian, Arabic, Pashto, Sindhi, Kashmiri) ===
        "ur": {"polyglossia": r"\setdefaultlanguage{urdu}", "font": r"\newfontfamily\urdufont{NotoNastaliqUrdu-Regular.ttf}[Path=../../Fonts/, Script=Arabic]"},
        "ar": {"polyglossia": r"\setdefaultlanguage{arabic}", "font": r"\newfontfamily\arabicfont{NotoNaskhArabic-Regular.ttf}[Path=../../Fonts/, Script=Arabic]"},
        "fa": {"polyglossia": r"\setdefaultlanguage{Persian}", "font": r"\setmainfont{NotoNaskhArabic-Regular.ttf}[Path=../../Fonts/, Script=Arabic]"},
        "ps": {"polyglossia": r"\setdefaultlanguage{pashto}", "font": r"\newfontfamily\pashtofont{NotoNaskhArabic-Regular.ttf}[Path=../../Fonts/, Script=Arabic]"},
        "sd": {"polyglossia": r"\setdefaultlanguage{sindhi}", "font": r"\newfontfamily\sindhifont{NotoNaskhArabic-Regular.ttf}[Path=../../Fonts/, Script=Arabic]"},
        "ks": {"polyglossia": r"\setdefaultlanguage{kashmiri}", "font": r"\newfontfamily\kashmirifont{NotoNaskhArabic-Regular.ttf}[Path=../../Fonts/, Script=Arabic]"},

        # === CJK Languages ===
        "zh-CN": {"polyglossia": r"\setdefaultlanguage{chinese}", "font": r"\newfontfamily\chinesefont{NotoSansSC-Regular.ttf}[Path=../../Fonts/]"},
        "zh-TW": {"polyglossia": r"\setdefaultlanguage{chinese}", "font": r"\newfontfamily\chinesefont{NotoSansTC-Regular.ttf}[Path=../../Fonts/]"},
        "ja": {
    "polyglossia": r"""\setdefaultlanguage{japanese}
    \XeTeXlinebreaklocale "ja"
    \XeTeXlinebreakskip=0pt plus 1pt""",
    "font": r"""\newfontfamily\japanesefont{NotoSansJP-Regular.ttf}[Path=../../Fonts/, Script=Kana, Language=Japanese]"""},
        "ko": {"polyglossia": r"\setdefaultlanguage{korean}", "font": r"\newfontfamily\koreanfont{NotoSansKR-Regular.ttf}[Path=../../Fonts/]"},

        # === Other scripts (Amharic, Armenian, Georgian, etc.) ===
        "am": {"polyglossia": r"\setdefaultlanguage{amharic}", "font": r"\newfontfamily\amharicfont{NotoSansEthiopic-Regular.ttf}[Path=../../Fonts/, Script=Ethiopic]"},
        "hy": {"polyglossia": r"\setdefaultlanguage{armenian}", "font": r"\newfontfamily\armenianfont{NotoSansArmenian-Regular.ttf}[Path=../../Fonts/, Script=Armenian]"},
        "ka": {"polyglossia": r"\setdefaultlanguage{georgian}", "font": r"\newfontfamily\georgianfont{NotoSansGeorgian-Regular.ttf}[Path=../../Fonts/, Script=Georgian]"},
        "si": {"polyglossia": r"\setdefaultlanguage{sinhala}", "font": r"\setmainfont{NotoSansSinhala-Regular.ttf}[Path=../../Fonts/, Script=Sinhala]"},
        "my": {"polyglossia": r"\setdefaultlanguage{burmese}", "font": r"\newfontfamily\burmesefont{NotoSansMyanmar-Regular.ttf}[Path=../../Fonts/, Script=Myanmar]"},
        "km": {"polyglossia": r"\setdefaultlanguage{khmer}", "font": r"\newfontfamily\khmerfont{NotoSansKhmer-Regular.ttf}[Path=../../Fonts/, Script=Khmer]"},
        "lo": {"polyglossia": r"\setdefaultlanguage{lao}", "font": r"\newfontfamily\laofont{NotoSansLao-Regular.ttf}[Path=../../Fonts/, Script=Lao]"},
        "mn": {"polyglossia": r"\setdefaultlanguage{mongolian}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/, Script=Cyrillic]"},
        "ti": {"polyglossia": r"\setdefaultlanguage{tigrinya}", "font": r"\newfontfamily\tigrinyafont{NotoSansEthiopic-Regular.ttf}[Path=../../Fonts/, Script=Ethiopic]"},

        # === Latin alphabet languages (Default fallback to NotoSans-Regular) ===
        "af": {"polyglossia": r"\setdefaultlanguage{afrikaans}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sq": {"polyglossia": r"\setdefaultlanguage{albanian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ay": {"polyglossia": r"\setdefaultlanguage{aymara}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "az": {"polyglossia": r"\setdefaultlanguage{azerbaijani}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "bm": {"polyglossia": r"\setdefaultlanguage{bambara}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "eu": {"polyglossia": r"\setdefaultlanguage{basque}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "be": {"polyglossia": r"\setdefaultlanguage{belarusian}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "bs": {"polyglossia": r"\setdefaultlanguage{bosnian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "bg": {"polyglossia": r"\setdefaultlanguage{bulgarian}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ca": {"polyglossia": r"\setdefaultlanguage{catalan}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ceb": {"polyglossia": r"\setdefaultlanguage{cebuano}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ny": {"polyglossia": r"\setdefaultlanguage{chichewa}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "co": {"polyglossia": r"\setdefaultlanguage{corsican}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "hr": {"polyglossia": r"\setdefaultlanguage{croatian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "cs": {"polyglossia": r"\setdefaultlanguage{czech}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "da": {"polyglossia": r"\setdefaultlanguage{danish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "dv": {"polyglossia": r"\setdefaultlanguage{dhivehi}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "doi": {"polyglossia": r"\setdefaultlanguage{dogri}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "nl": {"polyglossia": r"\setdefaultlanguage{dutch}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "en": {"polyglossia": r"\setdefaultlanguage{english}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "eo": {"polyglossia": r"\setdefaultlanguage{esperanto}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "et": {"polyglossia": r"\setdefaultlanguage{estonian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ee": {"polyglossia": r"\setdefaultlanguage{ewe}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "tl": {"polyglossia": r"\setdefaultlanguage{filipino}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "fi": {"polyglossia": r"\setdefaultlanguage{finnish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "fr": {"polyglossia": r"\setdefaultlanguage{french}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "fy": {"polyglossia": r"\setdefaultlanguage{frisian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "gl": {"polyglossia": r"\setdefaultlanguage{galician}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "de": {"polyglossia": r"\setdefaultlanguage{german}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "el": {"polyglossia": r"\setdefaultlanguage{greek}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ht": {"polyglossia": r"\setdefaultlanguage{haitian creole}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ha": {"polyglossia": r"\setdefaultlanguage{hausa}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "haw": {"polyglossia": r"\setdefaultlanguage{hawaiian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "iw": {"polyglossia": r"\setdefaultlanguage{hebrew}", "font": r"\newfontfamily\hebrewfont{NotoSansHebrew-Regular.ttf}[Path=../../Fonts/, Script=Hebrew]"},
        "hmn": {"polyglossia": r"\setdefaultlanguage{hmong}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "hu": {"polyglossia": r"\setdefaultlanguage{hungarian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "is": {"polyglossia": r"\setdefaultlanguage{icelandic}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ig": {"polyglossia": r"\setdefaultlanguage{igbo}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ilo": {"polyglossia": r"\setdefaultlanguage{ilocano}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "id": {"polyglossia": r"\setdefaultlanguage{indonesian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ga": {"polyglossia": r"\setdefaultlanguage{irish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "it": {"polyglossia": r"\setdefaultlanguage{italian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "jw": {"polyglossia": r"\setdefaultlanguage{javanese}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "kk": {"polyglossia": r"\setdefaultlanguage{kazakh}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "rw": {"polyglossia": r"\setdefaultlanguage{kinyarwanda}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "kri": {"polyglossia": r"\setdefaultlanguage{krio}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ku": {"polyglossia": r"\setdefaultlanguage{kurdish (kurmanji)}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ckb": {"polyglossia": r"\setdefaultlanguage{kurdish (sorani)}", "font": r"\setmainfont{NotoNaskhArabic-Regular.ttf}[Path=../../Fonts/, Script = Arabic]"},
        "ky": {"polyglossia": r"\setdefaultlanguage{kyrgyz}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "la": {"polyglossia": r"\setdefaultlanguage{latin}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "lv": {"polyglossia": r"\setdefaultlanguage{latvian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ln": {"polyglossia": r"\setdefaultlanguage{lingala}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "lt": {"polyglossia": r"\setdefaultlanguage{lithuanian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "lg": {"polyglossia": r"\setdefaultlanguage{luganda}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "lb": {"polyglossia": r"\setdefaultlanguage{luxembourgish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "mk": {"polyglossia": r"\setdefaultlanguage{macedonian}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/, Script=Cyrillic]"},
        "mg": {"polyglossia": r"\setdefaultlanguage{malagasy}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ms": {"polyglossia": r"\setdefaultlanguage{malay}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "mt": {"polyglossia": r"\setdefaultlanguage{maltese}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "mi": {"polyglossia": r"\setdefaultlanguage{maori}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "lus": {"polyglossia": r"\setdefaultlanguage{mizo}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "no": {"polyglossia": r"\setdefaultlanguage{norwegian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "om": {"polyglossia": r"\setdefaultlanguage{oromo}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "pl": {"polyglossia": r"\setdefaultlanguage{polish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "pt": {"polyglossia": r"\setdefaultlanguage{portuguese}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "qu": {"polyglossia": r"\setdefaultlanguage{quechua}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ro": {"polyglossia": r"\setdefaultlanguage{romanian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ru": {"polyglossia": r"\setdefaultlanguage{russian}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sm": {"polyglossia": r"\setdefaultlanguage{samoan}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "gd": {"polyglossia": r"\setdefaultlanguage{scots gaelic}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "nso": {"polyglossia": r"\setdefaultlanguage{sepedi}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sr": {"polyglossia": r"\setdefaultlanguage{serbian}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "st": {"polyglossia": r"\setdefaultlanguage{sesotho}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sn": {"polyglossia": r"\setdefaultlanguage{shona}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sk": {"polyglossia": r"\setdefaultlanguage{slovak}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sl": {"polyglossia": r"\setdefaultlanguage{slovenian}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "so": {"polyglossia": r"\setdefaultlanguage{somali}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "es": {"polyglossia": r"\setdefaultlanguage{spanish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "su": {"polyglossia": r"\setdefaultlanguage{sundanese}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sw": {"polyglossia": r"\setdefaultlanguage{swahili}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "sv": {"polyglossia": r"\setdefaultlanguage{swedish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "tg": {"polyglossia": r"\setdefaultlanguage{tajik}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "tt": {"polyglossia": r"\setdefaultlanguage{tatar}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "th": {"polyglossia": r"""\setdefaultlanguage{thai}\XeTeXlinebreaklocale "th" \XeTeXlinebreakskip = 0pt plus 1pt""","font": r"""\newfontfamily\thaifont{NotoSansThai-Regular.ttf}[Path=../../Fonts/, Script=Thai]"""},
        "ts": {"polyglossia": r"\setdefaultlanguage{tsonga}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "tr": {"polyglossia": r"\setdefaultlanguage{turkish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "tk": {"polyglossia": r"\setdefaultlanguage{turkmen}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ak": {"polyglossia": r"\setdefaultlanguage{twi}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "uk": {"polyglossia": r"\setdefaultlanguage{ukrainian}", "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "ug": {"polyglossia": r"\setdefaultlanguage{uyghur}", "font": r"\newfontfamily\uyghurfont{NotoNaskhArabic-Regular.ttf}[Path=../../Fonts/, Script=Arabic]"},
        "uz": {"polyglossia": r"\setdefaultlanguage{uzbek}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "vi": {"polyglossia": r"\setdefaultlanguage{vietnamese}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "cy": {"polyglossia": r"\setdefaultlanguage{welsh}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "xh": {"polyglossia": r"\setdefaultlanguage{xhosa}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "yi": {"polyglossia": r"\setdefaultlanguage{yiddish}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "yo": {"polyglossia": r"\setdefaultlanguage{yoruba}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
        "zu": {"polyglossia": r"\setdefaultlanguage{zulu}", "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../Fonts/]"},
    }
    return lang_map


# Load environment variables from .env file
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
# Serve compiled PDFs
app.mount("/static", StaticFiles(directory="temp"), name="static")


class GeminiRequest(BaseModel):
    prompt: Annotated[
        str, Field(..., title="Here, we can use Gemini", description="Enter prompt for the Gemini to compute....")]


class GroqRequest(BaseModel):
    prompt: Annotated[
        str, Field(..., title="Here, we can use Groq", description="Enter prompt for the Groq to compute....")]


class CoreRequest(BaseModel):
    prompt: Annotated[str, Field(..., title="Here, we can use Core for Research pages",
                                 description="Enter prompt for the Core to compute....")]

class LatexRequest(BaseModel):
    source: str

# Template configuration
templates = Jinja2Templates(directory="webTemplates")


# class ContentItem(BaseModel):
#     subContent: str
#     references: str


# class ContentBlock(BaseModel):
#     content: dict[str, ContentItem]

# class PulsusOutputStr(BaseModel):
#     content:  Annotated[ContentBlock,Field(..., title="This is the content block", description="Enter the stacks in the content blocks....")]

def add_business_days(start_date: datetime.date, days: int, brand: str) -> datetime.date:
    current_date = start_date

    if brand == 'hilaris.tex':
        # Just add calendar days
        current_date += datetime.timedelta(days=days)
        # If it lands on Saturday/Sunday, move to Monday
        while current_date.weekday() > 4:
            current_date += datetime.timedelta(days=1)
        return current_date

    else:
        # Count only weekdays
        added_days = 0
        while added_days < days:
            current_date += datetime.timedelta(days=1)
            if current_date.weekday() < 5:  # Mon-Fri
                added_days += 1
        return current_date


def format_date(date_obj: datetime.date) -> str:
    return date_obj.strftime("%d-%b-%Y")


class PulsusInputStr(BaseModel):
    id: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....",
                   max_length=6, min_length=3)]
    topic: Annotated[str, Field(..., title="Name of the topic", description="Enter the topic....")]
    journalName: Annotated[str, Field(..., title="Name of the journal where it belongs to.",
                                      description="Enter the journal where it belongs from...")]
    shortJournalName: Annotated[str, Field(..., title="Name of the short journal name where it belongs to.",
                                           description="Enter the short journal name where it belongs from...")]
    type: Annotated[str, Field(..., title="Name of the type(journal)", description="Enter the type of journal....")]
    author: Annotated[str, Field(..., title="Name of the author", description="Enter the author....")]
    email: Annotated[EmailStr, Field(..., title="Email of the author", description="Enter the autors email....")]
    brandName: Annotated[str, Field(..., title="Name of the brand", description="Enter the name of your brand...")]
    authorsDepartment: Annotated[
        str, Field(..., title="Department of the authour", description="Enter the department of the author....")]
    received: Annotated[
        str, Field(..., title="The receiving date", description="Enter the receiving date in DD-Mon format....")]
    manuscriptNo: Annotated[str, Field(..., title="The manuscriptNo of this journal",
                                       description="Enter the manuscriptNo for this journal....")]
    volume: Annotated[
        int, Field(..., title="The volume for the issue", description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[
        int, Field(..., title="The issue no. of the volume", description="Enter the issue no. of the volume...", gt=0)]
    pdfNo: Annotated[int, Field(..., title="The pdf number", description="Enter the pdf number....", gt=0)]
    doi: Annotated[Optional[str], Field(default="", title="DOI for this journal", description="Enter DOI for this Journal....")]
    ISSN: Annotated[
        Optional[str], Field(default=None, title="ISSN number of this journal", description="Enter the ISSN number for the journal....")]
    imgPath: Annotated[Optional[str], Field(default=None, title="image path", description="Enter the img path....")]
    parentLink: Annotated[AnyUrl, Field(..., title="The url for the centralized link",
                                        description="Enter the link which will led to the centralized page....")]


    editorAssigned: Optional[str] = None
    reviewed: Optional[str] = None
    revised: Optional[str] = None
    published: Optional[str] = None

    # Auto-populate extra dates after model init
    def model_post_init(self, __context):
        tempDate = []
        if self.brandName == "alliedAcademy.tex":
            tempDate = [2,14,7,7]
        else:
            tempDate = [2,14,5,7]
        received_date = datetime.datetime.strptime(self.received, "%Y-%m-%d").date()
        self.editorAssigned = format_date(add_business_days(received_date, tempDate[0], self.brandName))
        self.reviewed = format_date(add_business_days(received_date, tempDate[0] + tempDate[1], self.brandName))
        self.revised = format_date(add_business_days(received_date, tempDate[0] + tempDate[1] + tempDate[2], self.brandName))
        self.published = format_date(add_business_days(received_date, tempDate[0] + tempDate[1] + tempDate[2] + tempDate[3], self.brandName))
        self.received = format_date(received_date)

    @field_validator('pdfNo')
    @classmethod
    def validatePDFNo(cls, value):
        data = fetchInpData()
        for i in data.values():
            if value == i['pdfNo']:
                raise ValueError(f"Change the pdf page no. it is similar to the pdf artical name{i['topic']}")
        return value

    @computed_field
    @property
    def citeAuthorFormate(self) -> str:
        if self.brandName == 'hilaris.tex':
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 to 6 authors and seperated with comma). title of that journal inside double quotation. Journal short name Volume of the journal (year of publishing inside parenthesis):the page range or the number.end it with a full stop (for example: 'author n, author n, author n. "titleOFtheJournal." journalShortName Volume (year):ThePageRangeOrTheNumber.')"""

        elif self.brandName == 'alliedAcademy.tex':
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 or less, not more authors then that and seperated with comma). title of that journal. Journal short name. year of publishing;Volume of the journal:the page range or the number.(for example: 'author n, author n, author n. titleOFtheJournal. journalShortName. year;Volume:ThePageRangeOrTheNumber.')"""

        elif self.brandName == 'omics.tex':
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 to 6 authors and seperated with comma) (year of publishing inside parenthesis) title of that journal. Journal short name Volume of the journal:the page range or the number.(for example: 'author n, author n, author n (year) titleOFtheJournal. journalShortName Volume:ThePageRangeOrTheNumber')"""

        else:
            return """author names(first name + the remainings name's first letter(ex.: Arupa Nanda Swain then that should be Arupa NS) and there must be 3 or less, not more authors then that and seperated with comma). title of that journal. Journal short name. year of publishing;Volume of the journal:the page range or the number.(for example: 'author n, author n, author n. titleOFtheJournal. journalShortName. year;Volume:ThePageRangeOrTheNumber.')"""

class UpdateInputPartJournal(BaseModel):
    id: Annotated[Optional[str], Field(default=None, title="ID of the Input Journal",
                                       description="Enter the id for this journal input....")]
    topic: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    journalName: Annotated[Optional[str], Field(default=None, title="Name of the journal where it belongs to.",
                                                description="Enter the journal where it belongs from...")]
    shortJournalName: Annotated[
        Optional[str], Field(default=None, title="Name of the short journal name where it belongs to.",
                             description="Enter the short journal name where it belongs from...")]
    type: Annotated[Optional[str], Field(default=None, title="Name of the type(journal)",
                                         description="Enter the type of journal....")]
    author: Annotated[
        Optional[str], Field(default=None, title="Name of the author", description="Enter the author....")]
    email: Annotated[
        Optional[EmailStr], Field(default=None, title="Email of the author", description="Enter the autors email....")]
    brandName: Annotated[
        Optional[str], Field(default=None, title="Name of the brand", description="Enter the name of your brand...")]
    authorsDepartment: Annotated[Optional[str], Field(default=None, title="Department of the authour",
                                                      description="Enter the department of the author....")]
    received: Annotated[Optional[str], Field(default=None, title="The receiving date",
                                             description="Enter the receiving date in DD-Mon format....")]
    editorAssigned: Annotated[Optional[str], Field(default=None, title="The Editor Assigned date",
                                                   description="Enter the editor assigned date in DD-Mon format....")]
    reviewed: Annotated[Optional[str], Field(default=None, title="The journal review date",
                                             description="Enter the journal review date in DD-Mon format....")]
    revised: Annotated[Optional[str], Field(default=None, title="The journal revised date",
                                            description="Enter the journal revised date in DD-Mon format....")]
    published: Annotated[Optional[str], Field(default=None, title="The publishing date of journal",
                                              description="Enter the publishing date of the journal in DD-Mon format....")]
    manuscriptNo: Annotated[Optional[str], Field(default=None, title="The manuscriptNo of this journal",
                                                 description="Enter the manuscriptNo for this journal....")]
    volume: Annotated[Optional[int], Field(default=None, title="The volume for the issue",
                                           description="Enter the Volume of the issue...", gt=0)]
    issues: Annotated[Optional[int], Field(default=None, title="The issue no. of the volume",
                                           description="Enter the issue no. of the volume...", gt=0)]
    pdfNo: Annotated[
        Optional[int], Field(default=None, title="The pdf number", description="Enter the pdf number....", gt=0)]
    doi: Annotated[
        Optional[str], Field(default=None, title="DOI for this journal", description="Enter DOI for this Journal....")]
    ISSN: Annotated[Optional[str], Field(default=None, title="ISSN number of this journal",
                                         description="Enter the ISSN number for the journal....")]
    imgPath: Annotated[Optional[str], Field(default=None, title="image path", description="Enter the img path....")]
    parentLink: Annotated[Optional[AnyUrl], Field(default=None, title="The url for the centralized link",
                                                  description="Enter the link which will led to the centralized page....")]


class TranslatePage(BaseModel):
    id: Annotated[str, Field(..., title="The id of the page", description="Enter the id of the page....", min_length=3, max_length=6)]
    language: Annotated[str, Field(default=None, title="The language of the page", description="Enter the language of the page....")]



class ArticleItem(BaseModel):
    title: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    subContent: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    authors: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    published: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    doi: Annotated[Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    url: Annotated[Optional[AnyUrl], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    fulltextLinks: Annotated[
        Optional[List[str]], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    keywords: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]
    references: Annotated[
        Optional[str], Field(default=None, title="Name of the topic", description="Enter the topic....")]


class PulsusOutputStr(BaseModel):
    title: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    journalName: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    shortJournalName: Annotated[str, Field(..., title="Name of the short journal name where it belongs to.",
                                           description="Enter the short journal name where it belongs from...")]
    type: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    author: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    email: Annotated[
        EmailStr, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    brandName: Annotated[str, Field(..., title="Name of the brand", description="Enter the name of your brand...")]
    authorsDepartment: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    journalYearVolumeIssue: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    introduction: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    description: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    content: Annotated[Dict[str, Dict], Field(..., title="ID of the Input Journal",
                                              description="Enter the id for this journal input....")]
    abstract: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    keywords: Annotated[str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    doi: Annotated[
        Optional[str], Field(default=None, title="ID of the Input Journal", description="Enter the id for this journal input....")]
    received: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    editorAssigned: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    reviewed: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    revised: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    published: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    year: Annotated[int, Field(..., title="Yes of publishing", description="Enter the journal publising year...")]
    manuscriptNo: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    QCNo: Annotated[str, Field(..., title="The QC number", description="Enter the QC number....")]
    preQCNo: Annotated[str, Field(..., title="The preQC number", description="Enter the preQC number....")]
    RManuNo: Annotated[str, Field(..., title="The RManuNo number", description="Enter the RManuNo number....")]
    volume: Annotated[
        str, Field(..., title="The volume for the issue", description="Enter the Volume of the issue...")]
    issues: Annotated[
        str, Field(..., title="The issue no. of the volume", description="Enter the issue no. of the volume...")]
    ISSN: Annotated[Optional[str], Field(default="", title="ISSN Number", description="Enter the ISSN Number....")]
    imgPath: Annotated[Optional[str], Field(default=None, title="image path", description="Enter the img path....")]
    pdfNo: Annotated[int, Field(..., title="Pdf Number", description="Enter the PDF Number....")]
    parentLink: Annotated[
        AnyUrl, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]
    conclusion: Annotated[
        str, Field(..., title="ID of the Input Journal", description="Enter the id for this journal input....")]

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
    
    @computed_field
    @property
    def copyrightAuthor(self) -> str:
        copyAuth = self.author.split(' ')
        copyAuth = copyAuth[::-1]
        copyAuth[1] = f"{copyAuth[1][0]}."
        return " ".join(copyAuth)



    @computed_field
    @property
    def citation(self) -> str:
        if self.brandName == 'hilaris.tex':
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            justToCite[0] = f"{justToCite[0]}"
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite}. "{self.title}." {self.shortJournalName} {self.volume} ({self.published.split("-")[-1]}):{self.pdfNo}."""

        elif self.brandName == 'alliedAcademy.tex':
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite}. {self.title}. {self.shortJournalName}. {self.published.split("-")[-1]};{self.volume}({self.issues}):{self.pdfNo}."""

        elif self.brandName == 'omics.tex':
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite},({self.published.split("-")[-1]}) {self.title}. {self.shortJournalName} {self.volume}: {self.pdfNo}. DOI: {self.doi}"""
        
        else:
            justToCite = self.author.split(' ')
            justToCite.insert(0, justToCite[-1])
            justToCite = justToCite[0:-1]
            for i in range(1, len(justToCite)):
                justToCite[i] = justToCite[i][0]
            justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            return f"""{justToCite},({self.published.split("-")[-1]}) {self.title}. {self.shortJournalName} {self.volume}: {self.pdfNo}. DOI: {self.doi}"""




def fetchInpData():
    if not os.path.exists('journalDBInput.json'):
        return {}  # File doesn't exist → return empty dict

    with open('journalDBInput.json', 'r') as file:
        try:
            data = json.load(file)
            if not isinstance(data, dict):  # Ensure it's a dict
                return {}
            return data
        except json.JSONDecodeError:
            # File exists but is empty or invalid JSON
            return {}


def saveInpData(data):
    with open('journalDBInput.json', 'w') as file:
        if data is None:
            file = {}
        json.dump(data, file, default=str)


def fetchOutData():
    if not os.path.exists('journalDBOutput.json'):
        return {}  # File doesn't exist → return empty dict

    with open('journalDBOutput.json', 'r') as file:
        try:
            data = json.load(file)
            if not isinstance(data, dict):  # Ensure it's a dict
                return {}
            return data
        except json.JSONDecodeError:
            # File exists but is empty or invalid JSON
            return {}


def saveOutData(data):
    with open('journalDBOutput.json', 'w') as file:
        if data is None:
            file = {}
        json.dump(data, file, default=str)




def extract_json_from_markdown(text: str) -> str:
    """Extract JSON block from LLM markdown-style response."""
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    return text.strip()


def split_and_translate(text: str, dest_lang: str, max_len: int = 4900) -> str:
    """
    Splits text into chunks if it exceeds max_len,
    translates each chunk separately, and merges them.
    """
    if not text:
        return ""

    if len(text) <= max_len:
        return GoogleTranslator(source="auto", target=dest_lang).translate(text)

    paragraphs = text.split("\n\n")  # keep logical boundaries
    chunks, current = [], ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= max_len:
            current += para + "\n\n"
        else:
            chunks.append(current.strip())
            current = para + "\n\n"
    if current.strip():
        chunks.append(current.strip())

    translated_chunks = []
    for chunk in chunks:
        translated_chunks.append(GoogleTranslator(source="auto", target=dest_lang).translate(chunk))

    return "\n\n".join(translated_chunks)


def translate_text(input_dict, dest_lang):
    for key, value in input_dict.items():
        input_dict[key] = split_and_translate(value, dest_lang)
    return input_dict

@app.get("/")
def ui_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ui/about")
def ui_about(request: Request):
    return templates.TemplateResponse("aboutUs.html", {"request": request})


@app.get("/ui/add-journal")
def ui_add_journal(request: Request):
    return templates.TemplateResponse("addJournal.html", {"request": request})


@app.get("/ui/update-journal")
def ui_update_journal(request: Request):
    return templates.TemplateResponse("updateJournal.html", {"request": request})


@app.get("/ui/ask-gemini")
def ui_ask_gemini(request: Request):
    return templates.TemplateResponse("askGemini.html", {"request": request})


@app.get("/ui/ask-groq")
def ui_ask_groq(request: Request):
    return templates.TemplateResponse("askGroq.html", {"request": request})


@app.get("/ui/core-search")
def ui_core_search(request: Request):
    return templates.TemplateResponse("coreSearch.html", {"request": request})

@app.get("/ui/compile-latex")
def compile_latex(request: Request):
    return templates.TemplateResponse("latexEditor.html", {"request": request})

@app.post("/compile-latex")
def compile_latex(req: LatexRequest):
    job_id = str(uuid.uuid4())
    tex_file = f"temp/{job_id}.tex"
    pdf_file = f"temp/{job_id}.pdf"

    os.makedirs("temp", exist_ok=True)
    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(req.source)

    try:
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "-output-directory=temp", tex_file],
            check=True, capture_output=True, text=True
        )
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr}

    return {"pdf_path": f"/static/{job_id}.pdf"}


app.mount("/Logo", StaticFiles(directory="Logo"), name="Logo")


@app.get("/ui/pipeline")
def ui_pipeline(request: Request):
    image_files = []
    # Allowed image extensions
    allowed_ext = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg")

    for filename in os.listdir("Logo"):
        if filename.lower().endswith(allowed_ext):
            image_files.append(filename)

    return templates.TemplateResponse(
        "pipeline.html",
        {"request": request, "images": image_files}
    )

@app.get("/ui/translate")
def ui_translate(request: Request):
    languages = {"af" : "afrikaans",
    "sq" : "albanian",
    "am" : "amharic",
    "ar" : "arabic",
    "hy" : "armenian",
    "as" : "assamese",
    "ay" : "aymara",
    "az" : "azerbaijani",
    "bm" : "bambara",
    "eu" : "basque",
    "be" : "belarusian",
    "bn" : "bengali",
    "bho" : "bhojpuri",
    "bs" : "bosnian",
    "bg" : "bulgarian",
    "ca" : "catalan",
    "ceb" : "cebuano",
    "ny" : "chichewa",
    "zh-CN" : "chinese (simplified)",
    "zh-TW" : "chinese (traditional)",
    "co" : "corsican",
    "hr" : "croatian",
    "cs" : "czech",
    "da" : "danish",
    "dv" : "dhivehi",
    "doi" : "dogri",
    "nl" : "dutch",
    "en" : "english",
    "eo" : "esperanto",
    "et" : "estonian",
    "ee" : "ewe",
    "tl" : "filipino",
    "fi" : "finnish",
    "fr" : "french",
    "fy" : "frisian",
    "gl" : "galician",
    "ka" : "georgian",
    "de" : "german",
    "el" : "greek",
    "gu" : "gujarati",
    "ht" : "haitian creole",
    "ha" : "hausa",
    "haw" : "hawaiian",
    "iw" : "hebrew",
    "hi" : "hindi",
    "hmn" : "hmong",
    "hu" : "hungarian",
    "is" : "icelandic",
    "ig" : "igbo",
    "ilo" : "ilocano",
    "id" : "indonesian",
    "ga" : "irish",
    "it" : "italian",
    "ja" : "japanese",
    "jw" : "javanese",
    "kn" : "kannada",
    "kk" : "kazakh",
    "km" : "khmer",
    "rw" : "kinyarwanda",
    "gom" : "konkani",
    "ko" : "korean",
    "kri" : "krio",
    "ku" : "kurdish (kurmanji)",
    "ckb" : "kurdish (sorani)",
    "ky" : "kyrgyz",
    "lo" : "lao",
    "la" : "latin",
    "lv" : "latvian",
    "ln" : "lingala",
    "lt" : "lithuanian",
    "lg" : "luganda",
    "lb" : "luxembourgish",
    "mk" : "macedonian",
    "mai" : "maithili",
    "mg" : "malagasy",
    "ms" : "malay",
    "ml" : "malayalam",
    "mt" : "maltese",
    "mi" : "maori",
    "mr" : "marathi",
    "mni-Mtei" : "meiteilon (manipuri)",
    "lus" : "mizo",
    "mn" : "mongolian",
    "my" : "myanmar",
    "ne" : "nepali",
    "no" : "norwegian",
    "or" : "odia (oriya)",
    "om" : "oromo",
    "ps" : "pashto",
    "fa" : "persian",
    "pl" : "polish",
    "pt" : "portuguese",
    "pa" : "punjabi",
    "qu" : "quechua",
    "ro" : "romanian",
    "ru" : "russian",
    "sm" : "samoan",
    "sa" : "sanskrit",
    "gd" : "scots gaelic",
    "nso" : "sepedi",
    "sr" : "serbian",
    "st" : "sesotho",
    "sn" : "shona",
    "sd" : "sindhi",
    "si" : "sinhala",
    "sk" : "slovak",
    "sl" : "slovenian",
    "so" : "somali",
    "es" : "spanish",
    "su" : "sundanese",
    "sw" : "swahili",
    "sv" : "swedish",
    "tg" : "tajik",
    "ta" : "tamil",
    "tt" : "tatar",
    "te" : "telugu",
    "th" : "thai",
    "ti" : "tigrinya",
    "ts" : "tsonga",
    "tr" : "turkish",
    "tk" : "turkmen",
    "ak" : "twi",
    "uk" : "ukrainian",
    "ur" : "urdu",
    "ug" : "uyghur",
    "uz" : "uzbek",
    "vi" : "vietnamese",
    "cy" : "welsh",
    "xh" : "xhosa",
    "yi" : "yiddish",
    "yo" : "yoruba",
    "zu" : "zulu"
    }

    return templates.TemplateResponse(
        "translate.html",
        {"request": request, "languages": languages}
    )


@app.get("/ui/delete-journal")
def ui_delete_journal(request: Request):
    return templates.TemplateResponse("deleteJournal.html", {"request": request})


@app.get("/home")
def home():
    return {"message": "Automate the journals"}


@app.get("/about")
def aboutMe():
    return {
        "message": "This is a process where we are going to work with some Transformers APIs and that gonna lead us to a automation(by webscraping and more.)"}


@app.get("/view/journalInputData")
def viewTheData():
    data = fetchInpData()
    return f'{data}\n this is the journal data input.'


@app.get("/journalInputData/{JournalInputID}")
def fetchOneP(JournalInputID: str = Path(..., description='Enter your journal input index here....', examples="J001",
                                         max_length=4)):
    data = fetchInpData()
    if JournalInputID in data:
        return data[JournalInputID]
    raise HTTPException(status_code=404, detail='JOurnal input not found in DB')


@app.post("/addJournalInInput")
def createJournal(pulsusInput: PulsusInputStr):
    data = fetchInpData()
    if pulsusInput.id in data:
        raise HTTPException(status_code=400, detail="The id is already there.")
    data[pulsusInput.id] = pulsusInput.model_dump(exclude=["id"])
    saveInpData(data)
    return JSONResponse(status_code=200, content="Data Added successfully")


@app.put("/updateInputJournal/{JournalInputID}")
def updateInpJournal(JournalInputID: str, updateJor: UpdateInputPartJournal):
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

    return JSONResponse(status_code=200, content={"message": "Successfully updated"})


@app.delete("/delete/journalInputData/{JournalInputID}")
def deletePatient(JournalInputID):
    data = fetchInpData()
    if JournalInputID not in data:
        raise HTTPException(status_code=404, detail="Journal Not Found")

    del data[JournalInputID]

    saveInpData(data)

    return JSONResponse(status_code=200, content={"message": f"Perfectly deleted the {JournalInputID}"})


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
def pulsus_ask_groq(LLaMAAAAAAA: GroqRequest):
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

    print("Step 1 : Save journal input ✅")

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

    print("Step 2 : Use the topic to search CORE articles ✅")

    # Step 3: Create universal prompt
    prompt = f"""
    You are provided by a topic:
    topic : "{journal.topic}"


    Using this topic, generate a summarized structure that contains "subContent" (summary of key insights from the article), "references" (citation-style reference) and the remainings and make sure all the journals are authentic not created by you and have more then or equal to 3 authors, and i need recent year data's(last 5 years) and must from a legit author and the links must work properly, don't provide any dummy data or dummy link.


    The final structure should look like:
    "content": {{
      "C001": {{
        "subContent": "...",
        "references": "...", # make sure that cite should be in {journal.citeAuthorFormate} formate
        "title": "...",
        "journalShortName": "...",
        "authors": ["...", "...", "..."], #only three authors name (full name)
        "published": "...",
        "pageRangeOrNumber": "...", #the page range or the page number
        "volume": "...",
        "issues": "...",
        "DOI": "...",
        "url": "...", # pubmed link of the journal
        "parentLink": "..." # the perticular article link
      }}, # give me exact 10 References(..., C009, C010)
      ...
    }}


    Focus on creating references from title, authors, year, and DOI.
    the most important thing, and the whole data will be copied out and used so give me clean information only the structured data no other thing not even a symbol or dot.
    note: Write like a confident, clear thinking human speaking to another smart human.
        Avoid robotic phrases like 'in today's fast-paced world', 'leveraging synergies', or
        'furthermore.
        Skip unnecessary dashes (-), quotation marks (''), and corporate buzzwords like 'cutting-edge', 'robust', or 'seamless experience. No Al tone. No fluff. No filler.
        Use natural transitions like 'here's the thing', 'let's break it down; or 'what this really means is' Keep sentences varied in length and rhythm, like how real people speak or write. Prioritize clarity, personality, and usefulness.
        Every sentence should feel intentional, not generated
    IMPORTANT: Your response must be ONLY a valid JSON object with no additional text, 
        explanations, or markdown formatting. Do not include any text before or after the JSON.
    """
    print("Step 3 : Create universal prompt ✅")
    # Step 4: Ask Gemini
    for i in range(3):
        gem_response = None
        for j in range(3):
            try:
                gem_response = gemClient.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )
                gem_summary = gem_response.text
                print(f"The text generation attempt{j}")
                break
            except Exception as e:
                print(f"The text generation attempt{j} failed {str(e)}")
                gem_summary = f"Gemini API failed: {str(e)}"
                print("WAITING FOR 3 SECONDS...")
                time.sleep(3)
                if j == 2:
                    raise HTTPException(status_code=500, detail=gem_summary)

        print("step 4 : ask Gemini ✅")

        # Step 5: Clean and parse JSON output from Gemini
        raw_json = extract_json_from_markdown(gem_summary)
        print(f"The parsing attempt{i}")

        try:
            parsed = json.loads(raw_json)
            content_data = parsed["content"]
            gemClient.models.generate_content(
                model="gemini-2.5-flash", contents="the previous response was on point respond me in (my pleasure / i am happy)"
            )
            break
        except Exception as e:
            print(f"The parsing attempt{i} failed {str(e)}")
            prompt = (
                """Your last response was not valid JSON.
                IMPORTANT: Respond with valid JSON. No additional text, explanations, or formatting."""
            )
            if i == 2:
                raise HTTPException(status_code=500, detail=f"Failed to parse structured JSON from LLM output: {str(e)}")
    

    
    for kk in content_data.keys():
        store = []
        for i in content_data[kk]["authors"]:
            justToCite = i.split(' ')
            if len(justToCite) != 1:
                for i in range(1, len(justToCite)):
                    justToCite[i] = justToCite[i][0]
                justToCite[1] = " " + justToCite[1]
            justToCite = "".join(justToCite)
            store.append(justToCite)
        content_data[kk]["authors"] = ", ".join(store)


    print("Step 5 : Clean and parse JSON output from Gemini ✅")

    # Step 6: Conclusion content using Gemini
    prompt = f"""
    This is the given data : "{content_data}"
    i want to you to process this data and give me some output:
    1: Give me a brief summary from the given data where the word count lies in between 200 - 400.
    2: Give me a brief introduction from the given data where it will contain the citation markers as well, and note, you have to take in this way: the "C001" will be 1, "C002": 2...... and each section should have different but sequential citation markers (for ex: "C001" will be [1], "C002": [2] and so on). and give two linebreak '\n' after the citation marker and also make sure the citation marker must stays before the full stop '.' and covered with square brackets'[]'(for ex: [1], [2]....., [10]), and the full introduction word count lies in between 600 - 800.
    3: Give me a brief description from the given data and note, the full description contain more then 4 paragraphs with word count lies in between 600 - 800 NOTE: Add citation markers(Inside square brackets).
    4: Give me a abstract from the given data, and the full abstract word count lies in between 90 - 100.

    The final structure should look like:
    "content": {{
      "introduction": '''...''',
      "description" : '''...''',
      "summary" : '''...''',
      "abstract" : '''...''',
      "keywords" : '''...''' # give me Minimun 5 to 10 keywords joined by comma(,)
      ...
    }}


    note: Do not include any introductory labels, brand names, or meta-commentary. Remove all special characters, escape sequences, and formatting symbols. Respond only with plain and clean text containing the summary. Respond without any introductory phrases, labels, brand mentions, or headings (e.g., 'Summary:', 'Gemini:', 'Groq:'). Do not include explanations of how you generated the answer unless explicitly asked.
        Write like a confident, clear thinking human speaking to another smart human.
        Avoid robotic phrases like 'in today's fast-paced world', 'leveraging synergies', 'furthermore'.....
        Skip unnecessary dashes (-), quotation marks (''), and corporate buzzwords like 'cutting-edge', 'robust', or 'seamless experience. No Al tone. No fluff. No filler.
        Use natural transitions like 'here's the thing', ‘let's break it down; or ‘what this really means is’ Keep sentences varied in length and rhythm, like how real people speak or write. Prioritize clarity, personality, and usefulness.
        Every sentence should feel intentional, not generated. And Short names/abbreviations should be in Title case (e.g., Artificial Intelligence (AI))
    IMPORTANT: Your response must be ONLY a valid JSON object with no additional text, 
        explanations, or markdown formatting. Do not include any text before or after the JSON.
"""
    for i in range(3):
        gem_response = None
        for j in range(3):
            try:
                gem_response = gemClient.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )
                print(f"The text generation attempt{j}")
                gem_info = gem_response.text
                break
            except Exception as e:
                gem_info = f"Gemini API failed: {str(e)}"
                print(f"The text generation attempt{j} failed: {str(e)}")
                print("WAITING FOR 3 SECONDS...")
                time.sleep(3)
                if j == 2:
                    raise HTTPException(status_code=500, detail=f"Gemini API failed: {str(e)}")

        print("step 6 : Conclusion content using Gemini ✅")

        # Step 6.5: Clean and parse JSON output from Gemini or Groq
        raw_json = extract_json_from_markdown(gem_info)
        print(f"The parsing attempt{i}")

        try:
            parsed = json.loads(raw_json)
            gem_info = parsed["content"]
            break
        except Exception as e:
            print(f"The parsing attempt{i} failed {str(e)}")
            prompt = (
                "Your last response was not valid JSON. "
                "Please return ONLY valid JSON, no markdown, no extra text."
            )
            if i == 2:
                raise HTTPException(status_code=500, detail=f"Failed to parse structured JSON from LLM output: {str(e)}")
            
    gemClient.models.generate_content(
        model="gemini-2.5-flash", contents="the previous response was on point respond me in (my pleasure / i am happy)"
    )
    print("step 6.5 : Clean and parse JSON output from Gemini or Groq ✅")

    # Step 7: Title content using Gemini
    
    prompt = f"""
    Generate a 5-7 word title based on this summary: {gem_info.get('summary', '')}
    
    IMPORTANT: Respond with ONLY the title. No additional text, explanations, or formatting.
    """
    gem_response = None
    for i in range(3):
        try:
            print(f"The text generation attempt{j}")
            gem_response = gemClient.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            gem_title = gem_response.text
            break
        except Exception as e:
            print(f"The text generation attempt{j} failed: {str(e)}")
            print("WAITING FOR 3 SECONDS...")
            time.sleep(3)
            gem_title = f"Gemini API failed: {str(e)}"
            if i == 2:
                raise HTTPException(status_code=500, detail=f"Gemini API failed: {str(e)}")

    print("step 7 : Title content using Gemini ✅")
    if journal.brandName == "alliedAcademy.tex":
        storeTempTitle = gem_title.split(": ")
        if len(storeTempTitle) != 1:
            count = 0
            for i in storeTempTitle:
                storeTempTitle[count] = i.capitalize()
                count += 1
            gem_title = ": ".join(storeTempTitle)
        else:
            gem_title = gem_title.capitalize()
        storeTempTitle = None

    # Step 8: Final response
    final_output = {
        journal.id: {
            "title": gem_title[:-1],
            "journalName": journal.journalName,
            "shortJournalName": journal.shortJournalName,
            "type": journal.type,
            "author": journal.author,
            "email": journal.email,
            "brandName": journal.brandName,
            "authorsDepartment": journal.authorsDepartment,
            "journalYearVolumeIssue": f"{journal.shortJournalName}, Volume {journal.volume}:{journal.issues}, {journal.published.split('-')[-1]}",
            "introduction": gem_info["introduction"],
            "description": gem_info["description"],
            "abstract": gem_info["abstract"],
            "keywords": gem_info["keywords"],
            "content": content_data,
            "doi": journal.doi,
            "received": journal.received,
            "editorAssigned": journal.editorAssigned,
            "reviewed": journal.reviewed,
            "revised": journal.revised,
            "published": journal.published,
            "year": int(journal.published.split('-')[-1]),
            "manuscriptNo": journal.manuscriptNo,
            "QCNo": f"Q-{journal.manuscriptNo.split('-')[-1]}" if journal.brandName == "hilaris.tex" else journal.manuscriptNo,
            "preQCNo": f"P-{journal.manuscriptNo.split('-')[-1]}" if journal.brandName == "hilaris.tex" else journal.manuscriptNo,
            "RManuNo": f"R-{journal.manuscriptNo.split('-')[-1]}" if journal.brandName == "hilaris.tex" else journal.manuscriptNo,
            "volume": f"0{journal.volume}" if len(str(journal.volume))==1 else str(journal.volume),
            "issues": f"0{journal.issues}" if len(str(journal.issues))==1 else str(journal.issues),
            "pdfNo": journal.pdfNo,
            "ISSN": journal.ISSN,
            "imgPath": journal.imgPath,
            "parentLink": str(journal.parentLink),
            "conclusion": gem_info["summary"]
        }
    }

    saveInpData(data)

    output_data = fetchOutData()
    pulsus_output_instance = PulsusOutputStr(**final_output[journal.id])
    output_data[journal.id] = pulsus_output_instance.model_dump()
    saveOutData(output_data)

    # =========================================================================
    # File Generation Section
    # =========================================================================

    # --- Centralized Directory Setup ---
    # Create a single directory for all of this journal's output files.
    output_base_dir = pathOfPathLib("PDFStorePulsus")
    journal_folder = output_base_dir / journal.id
    journal_folder.mkdir(parents=True, exist_ok=True)

    print("Step 8 : Final response ✅")

    # --- 9: Create HTML file ---
    env_html = Environment(
        loader=FileSystemLoader(pathOfPathLib("./templates/"))
    )
    try:
        html_template = env_html.get_template("Format.html")
        forHtml = copy.deepcopy(output_data[journal.id])

        # Logic for processing references for HTML
        
        for i in range(1, len(forHtml["content"]) + 1):
            forHtml["introduction"] = forHtml["introduction"].replace(f"[{i}].",
                                                                      f"[<a href='#{i}' title='{i}'>{i}</a>].</p><p>")

        forHtml["description"] = forHtml["description"].replace("\n\n", "</p><p>")
        forHtml["description"] = forHtml["description"].replace("\n", "</p><p>")
        
        storeBody = {}
        
        if journal.brandName == "alliedAcademy.tex":
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Conclusion"] = forHtml["conclusion"]
        elif journal.brandName == "omics.tex":
            storeBody["Abstract"] = forHtml["abstract"]
            storeBody["Keywords"] = forHtml["keywords"]
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]
        elif journal.brandName == "hilaris.tex":
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]
            storeBody["Acknowledgement"] = None
            storeBody["Conflict_of_Interest"] = None
        elif journal.brandName == "iomc.tex":
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]
        else :
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]
            
        forHtml["storeBody"] = storeBody

        count = 0
        forHtml["storeRefPart"] = ""
        for i in forHtml["content"].values():
            count += 1
            i["issues"] = f"({i['issues']})" if i.get("issues") else ""

            if journal.brandName == "alliedAcademy.tex":
                temp = f"""<li><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>. {i["journalShortName"]}. {i["published"]};{i["volume"]}{i["issues"]}:{i["pageRangeOrNumber"]}.</li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
            elif journal.brandName == "omics.tex":
                temp = f"""<li><a name="{count}" id="{count}"></a>{i["authors"]} ({i["published"]}) <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>.{i["journalShortName"]} {i["volume"]}:{i["pageRangeOrNumber"]}.</li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
            elif journal.brandName == "hilaris.tex":
                temp = f"""<li><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">"{i["title"]}"</a>.<i>{i["journalShortName"]}</i> {i["volume"]} ({i["published"]}):{i["pageRangeOrNumber"]}.</li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
            else:
                temp = f"""<li><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>. {i["journalShortName"]}. {i["published"]};{i["volume"]}{i["issues"]}:{i["pageRangeOrNumber"]}.</li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""

            forHtml["storeRefPart"] = f"""{forHtml['storeRefPart']}\n{temp}"""

        department_parts = forHtml['authorsDepartment'].split(',')
        if len(department_parts) > 1:
            forHtml["prefixAuthorDepartment"] = f"{department_parts[0]}<br />"
            forHtml["suffixAuthorDepartment"] = f"{','.join(department_parts[1:])}.<br />"
        else:
            forHtml["prefixAuthorDepartment"] = forHtml['authorsDepartment']
            forHtml["suffixAuthorDepartment"] = "<br />"

        rendered_html = html_template.render(**forHtml)

        # Save the HTML file inside the journal's dedicated folder
        html_file_path = journal_folder / f"{journal.id}.html"
        html_file_path.write_text(rendered_html, encoding="utf-8")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate HTML file: {str(e)}")

    print("Step 9 : Created HTML file ✅")

    # --- 10: Create PDF file ---
    env_latex = Environment(
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
        loader=FileSystemLoader(pathOfPathLib("./templates"))
    )

    def latex_escape(text):
        if not isinstance(text, str):
            return text
        replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '^': r'\^{}',
        '~': r'\textasciitilde{}',
        '\\': r'\textbackslash{}',
    }
        pattern = re.compile('|'.join(re.escape(k) for k in replacements.keys()))
        return pattern.sub(lambda m: replacements[m.group()], text)
    
    def format_reference(ref: str) -> str:
        if not isinstance(ref, str):
            return ref
        
        # First escape LaTeX
        ref = latex_escape(ref)

        # Regex: Find journal short name (before year/volume/semicolon/parenthesis)
        # Example match: " J. Biomol. Struct. Dyn"
        pattern = r"(\s)([A-Z][A-Za-z\.\s]+)(?=\s\d|\s\(|;)"
        
        def repl(match):
            return f" \\textit{{{match.group(2).strip()}}}"

        return re.sub(pattern, repl, ref, count=1)
    
    env_latex.filters['format_reference'] = format_reference
    template = env_latex.get_template(journal.brandName)
    
    brand_key = journal.brandName.replace(".tex", "")
    lang_map = get_lang_map(brand_key)

    # --- ensure initial PDF has an English preamble and mark language in saved record ---
    default_cfg = lang_map.get("default")
    # Build preamble: polyglossia + the font block stored in default_cfg
    preamble = "\\usepackage{polyglossia}\n" + default_cfg["polyglossia"] + "\n" + default_cfg["font"]
    output_data[journal.id]["preamble"] = preamble
    output_data[journal.id]["lang_name"] = "english"
    # record original language so later translation flow can detect existing language if needed
    output_data[journal.id]["lang"] = "en"

    rendered_latex = template.render(**output_data[journal.id])

    # Save the .tex file inside the journal's dedicated folder
    tex_file_path = journal_folder / f"{journal.id}.tex"
    tex_file_path.write_text(rendered_latex, encoding="utf-8")

    # Compile LaTeX to PDF. Run from within the journal's folder.
    for i in range(2):
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", tex_file_path.name],
            capture_output=True,  # Capture stdout/stderr
            text=True,
            cwd=journal_folder  # CRITICAL: Set the working directory
        )

        if result.returncode != 0:
            log_file_path = tex_file_path.with_suffix(".log")

            # The log file is already saved by xelatex, so we just read it for the error message
            error_text = "Unknown LaTeX error. Check the log file."
            if log_file_path.exists():
                with open(log_file_path, 'r') as f:
                    lines = f.readlines()
                error_snippets = [line for line in lines if line.startswith("! ")]
                error_text = "\n".join(error_snippets) or f"LaTeX compilation failed. Full log in {log_file_path}"

            raise HTTPException(
                status_code=500,
                detail=f"LaTeX compilation failed on run {i + 1}:\n\n{error_text}"
            )

    print("Step 10 : Create PDF file ✅")

    return JSONResponse(
        status_code=200,
        content={"Status": f"Data added and files generated successfully in PDFStorePulsus/{journal.id}/ ✅."}
    )
    

#-----------------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------------


@app.post("/pdfs/translate")
async def pdfs_translate(translatePage : TranslatePage):
    
    print("Start the process of translation ✅")

    output_data = fetchOutData()
    if translatePage.id not in output_data:
        details = "Journal ID doesn't exists. id's present are : "
        for i in output_data.keys():
            details = f"{details} {i}"
        raise HTTPException(status_code=404, detail = details)

    journal_id = output_data[translatePage.id]

    tempStore = {
    "introduction": journal_id['introduction'],
    "description": journal_id['description'],
    "abstract": journal_id['abstract'],
    "keywords": journal_id['keywords'],
    "conclusion": journal_id['conclusion']
    }
    print("Step 1: Start Translation ✅")
    tempStore = translate_text(tempStore, translatePage.language)


    for i,j in tempStore.items():
        journal_id[i] = j



    # =========================================================================
    # File Generation Section
    # =========================================================================

    # --- Centralized Directory Setup ---
    # Create a single directory for all of this journal's output files.
    output_base_dir = pathOfPathLib("PDFTranslatedStorePulsus")
    journal_folder = output_base_dir / f"{translatePage.language}_translate_{translatePage.id}"
    journal_folder.mkdir(parents=True, exist_ok=True)

    print("Step 2: Final response ✅")

    # --- 9: Create HTML file ---
    env_html = Environment(
        loader=FileSystemLoader(pathOfPathLib("./templates/"))
    )
    try:
        html_template = env_html.get_template("Format1.html")
        forHtml = copy.deepcopy(journal_id)

        # Logic for processing references for HTML

        for i in range(1, len(forHtml["content"]) + 1):
            forHtml["introduction"] = forHtml["introduction"].replace(f"[{i}].",
                                                                      f"[<a href='#{i}' title='{i}'>{i}</a>].</p><p>")
            forHtml["description"] = forHtml["description"].replace(f"[{i}].",
                                                                      f"[<a href='#{i}' title='{i}'>{i}</a>].")

        forHtml["description"] = forHtml["description"].replace("\n\n", "</p><p>")
        forHtml["description"] = forHtml["description"].replace("\n", "</p><p>")

        storeBody = {}

        if journal_id['brandName'] == "alliedAcademy.tex":
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Conclusion"] = forHtml["conclusion"]
        elif journal_id['brandName'] == "omics.tex":
            storeBody["Abstract"] = forHtml["abstract"]
            storeBody["Keywords"] = forHtml["keywords"]
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]
        elif journal_id['brandName'] == "hilaris.tex":
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]
            storeBody["Acknowledgement"] = None
            storeBody["Conflict_of_Interest"] = None
        elif journal_id['brandName'] == "iomc.tex":
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]
        else:
            storeBody["Introduction"] = forHtml["introduction"]
            storeBody["Description"] = forHtml["description"]
            storeBody["Conclusion"] = forHtml["conclusion"]

        forHtml["storeBody"] = storeBody

        count = 0
        forHtml["storeRefPart"] = ""
        for i in forHtml["content"].values():
            count += 1
            i["issues"] = f"({i['issues']})" if i.get("issues") else ""

            if journal_id['brandName'] == "alliedAcademy.tex":
                temp = f"""<li><i><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>. {i["journalShortName"]}. {i["published"]};{i["volume"]}{i["issues"]}:{i["pageRangeOrNumber"]}.</i></li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
            elif journal_id['brandName'] == "omics.tex":
                temp = f"""<li><i><a name="{count}" id="{count}"></a>{i["authors"]} ({i["published"]}) <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>.{i["journalShortName"]} {i["volume"]}:{i["pageRangeOrNumber"]}.</i></li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
            elif journal_id['brandName'] == "hilaris.tex":
                temp = f"""<li><i><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">"{i["title"]}"</a>.<i>{i["journalShortName"]}</i> {i["volume"]} ({i["published"]}):{i["pageRangeOrNumber"]}.</i></li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
            else:
                temp = f"""<li><i><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>. {i["journalShortName"]}. {i["published"]};{i["volume"]}{i["issues"]}:{i["pageRangeOrNumber"]}.</i></li>
                <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""

            forHtml["storeRefPart"] = f"""{forHtml['storeRefPart']}\n{temp}"""

        department_parts = forHtml['authorsDepartment'].split(',')
        if len(department_parts) > 1:
            forHtml["prefixAuthorDepartment"] = f"{department_parts[0]}<br />"
            forHtml["suffixAuthorDepartment"] = f"{','.join(department_parts[1:])}.<br />"
        else:
            forHtml["prefixAuthorDepartment"] = forHtml['authorsDepartment']
            forHtml["suffixAuthorDepartment"] = "<br />"

        rendered_html = html_template.render(**forHtml)

        # Save the HTML file inside the journal's dedicated folder
        html_file_path = journal_folder / f"{translatePage.id}.html"
        html_file_path.write_text(rendered_html, encoding="utf-8")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate HTML file: {str(e)}")

    print("Step 3 : Create HTML file ✅")

    # --- 10: Create PDF file ---
    env_latex = Environment(
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
        loader=FileSystemLoader(pathOfPathLib("./templates"))
    )

    def latex_escape(text):
        if not isinstance(text, str):
            return text
        replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '^': r'\^{}',
        '~': r'\textasciitilde{}',
        '\\': r'\textbackslash{}',
    }
        pattern = re.compile('|'.join(re.escape(k) for k in replacements.keys()))
        return pattern.sub(lambda m: replacements[m.group()], text)
    
    def format_reference(ref: str) -> str:
            if not isinstance(ref, str):
                return ref
            
            # First escape LaTeX
            ref = latex_escape(ref)

            # Regex: Find journal short name (before year/volume/semicolon/parenthesis)
            # Example match: " J. Biomol. Struct. Dyn"
            pattern = r"(\s)([A-Z][A-Za-z\.\s]+)(?=\s\d|\s\(|;)"
            
            def repl(match):
                return f" \\textit{{{match.group(2).strip()}}}"

            return re.sub(pattern, repl, ref, count=1)
        
    env_latex.filters['format_reference'] = format_reference
    template = env_latex.get_template(journal_id['brandName'])

    brand_key = journal_id['brandName'].replace(".tex", "")
    lang_map = get_lang_map(brand_key)

    # Use the language passed in request (translatePage.language) as the target
    target_lang = translatePage.language or output_data[translatePage.id].get("lang", "en")
    lang_config = lang_map.get(target_lang, lang_map["default"])

    # Extract a language name (e.g. 'hindi' from '\setdefaultlanguage{hindi}' etc.)
    match = re.search(r"\{(.*?)\}", lang_config.get("polyglossia",""))
    lang_name = match.group(1) if match else target_lang

    # Build preamble for the translated PDF:
    # For translated files we want the document default language to be the target language
    if target_lang in ("default", "en", "english"):
        # keep english default (Times New Roman main font is already present in template)
        preamble = "\\usepackage{polyglossia}\n" + r"\setdefaultlanguage{english}" + "\n" + lang_map["default"]["font"]
    else:
        # Set the document's default to the target language and include the font declarations
        preamble = "\\usepackage{polyglossia}\n" + f"\\setdefaultlanguage{{{lang_name}}}\n" + lang_config["font"]

    # Inject into template variables (so template sees \VAR{preamble} and \VAR{lang_name})
    output_data[translatePage.id]["preamble"] = preamble
    output_data[translatePage.id]["lang_name"] = lang_name

    # (Optional) record that the output is now in this language:
    output_data[translatePage.id]["lang"] = target_lang

    rendered_latex = template.render(**output_data[translatePage.id])

    # Save the .tex file inside the journal's dedicated folder
    tex_file_path = journal_folder / f"{translatePage.id}.tex"
    tex_file_path.write_text(rendered_latex, encoding="utf-8")

    # Compile LaTeX to PDF. Run from within the journal's folder.
    for i in range(2):
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", tex_file_path.name],
            capture_output=True,  # Capture stdout/stderr
            text=True,
            encoding="utf-8",
            cwd=journal_folder  # CRITICAL: Set the working directory
        )

        if result.returncode != 0:
            log_file_path = tex_file_path.with_suffix(".log")

            # The log file is already saved by xelatex, so we just read it for the error message
            error_text = "Unknown LaTeX error. Check the log file."
            if log_file_path.exists():
                with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                error_snippets = [line for line in lines if line.startswith("! ")]
                error_text = "\n".join(error_snippets) or f"LaTeX compilation failed. Full log in {log_file_path}"


            raise HTTPException(
                status_code=500,
                detail=f"LaTeX compilation failed on run {i + 1}:\n\n{error_text}"
            )

    print("Final Step: Create PDF file ✅")

    return JSONResponse(
        status_code=200,
        content={"Status": f"Data added and files generated successfully in PDFTranslatedStorePulsus/{translatePage.id}/ ✅."}
    )
