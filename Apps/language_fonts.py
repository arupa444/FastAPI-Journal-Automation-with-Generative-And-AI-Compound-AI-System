# File: Apps/language_fonts.py
from re import L
from .library_import import pathOfPathLib

languages = {
    "af": "afrikaans",
    "sq": "albanian",
    "am": "amharic",
    "ar": "arabic",
    "hy": "armenian",
    "as": "assamese",
    "ay": "aymara",
    "az": "azerbaijani",
    "bm": "bambara",
    "eu": "basque",
    "be": "belarusian",
    "bn": "bengali",
    "bho": "bhojpuri",
    "bs": "bosnian",
    "bg": "bulgarian",
    "ca": "catalan",
    "ceb": "cebuano",
    "ny": "chichewa",
    "zh-CN": "chinese (simplified)",
    "zh-TW": "chinese (traditional)",
    "co": "corsican",
    "hr": "croatian",
    "cs": "czech",
    "da": "danish",
    "dv": "dhivehi",
    "doi": "dogri",
    "nl": "dutch",
    "en": "english",
    "eo": "esperanto",
    "et": "estonian",
    "ee": "ewe",
    "tl": "filipino",
    "fi": "finnish",
    "fr": "french",
    "fy": "frisian",
    "gl": "galician",
    "ka": "georgian",
    "de": "german",
    "el": "greek",
    "gu": "gujarati",
    "ht": "haitian creole",
    "ha": "hausa",
    "haw": "hawaiian",
    "iw": "hebrew",
    "hi": "hindi",
    "hmn": "hmong",
    "hu": "hungarian",
    "is": "icelandic",
    "ig": "igbo",
    "ilo": "ilocano",
    "id": "indonesian",
    "ga": "irish",
    "it": "italian",
    "ja": "japanese",
    "jw": "javanese",
    "kn": "kannada",
    "kk": "kazakh",
    "km": "khmer",
    "rw": "kinyarwanda",
    "gom": "konkani",
    "ko": "korean",
    "kri": "krio",
    "ku": "kurdish (kurmanji)",
    "ckb": "kurdish (sorani)",
    "ky": "kyrgyz",
    "lo": "lao",
    "la": "latin",
    "lv": "latvian",
    "ln": "lingala",
    "lt": "lithuanian",
    "lg": "luganda",
    "lb": "luxembourgish",
    "mk": "macedonian",
    "mai": "maithili",
    "mg": "malagasy",
    "ms": "malay",
    "ml": "malayalam",
    "mt": "maltese",
    "mi": "maori",
    "mr": "marathi",
    "mni-Mtei": "meiteilon (manipuri)",
    "lus": "mizo",
    "mn": "mongolian",
    "my": "myanmar",
    "ne": "nepali",
    "no": "norwegian",
    "or": "odia (oriya)",
    "om": "oromo",
    "ps": "pashto",
    "fa": "persian",
    "pl": "polish",
    "pt": "portuguese",
    "pa": "punjabi",
    "qu": "quechua",
    "ro": "romanian",
    "ru": "russian",
    "sm": "samoan",
    "sa": "sanskrit",
    "gd": "scots gaelic",
    "nso": "sepedi",
    "sr": "serbian",
    "st": "sesotho",
    "sn": "shona",
    "sd": "sindhi",
    "si": "sinhala",
    "sk": "slovak",
    "sl": "slovenian",
    "so": "somali",
    "es": "spanish",
    "su": "sundanese",
    "sw": "swahili",
    "sv": "swedish",
    "tg": "tajik",
    "ta": "tamil",
    "tt": "tatar",
    "te": "telugu",
    "th": "thai",
    "ti": "tigrinya",
    "ts": "tsonga",
    "tr": "turkish",
    "tk": "turkmen",
    "ak": "twi",
    "uk": "ukrainian",
    "ur": "urdu",
    "ug": "uyghur",
    "uz": "uzbek",
    "vi": "vietnamese",
    "cy": "welsh",
    "xh": "xhosa",
    "yi": "yiddish",
    "yo": "yoruba",
    "zu": "zulu",
}


class LatexLanguageConfig:
    """
    Manage LaTeX language and font configurations.
    """

    # Define it as a class-level variable
    brand_fonts = {
        "default": r"""
        \usepackage{fontspec}
        \setmainfont{Times New Roman}[
            Path=../../../Fonts/,
            UprightFont    = * ,
            BoldFont       = *-Bold ,
            ItalicFont     = *-Italic ,
            BoldItalicFont = *-BoldItalic
        ]""",
        "alliedAcademy": r"""
        \usepackage{fontspec}
        \setmainfont{Times New Roman}[
            Path=../../../Fonts/,
            UprightFont    = * ,
            BoldFont       = *-Bold ,
            ItalicFont     = *-Italic ,
            BoldItalicFont = *-BoldItalic
        ]""",
        "hilaris": r"""
        \usepackage{fontspec}
        \setmainfont{ArchivoNarrow}[
            Path=../../../Fonts/,
            UprightFont    = *-Regular ,
            BoldFont       = *-Bold ,
            ItalicFont     = *-Italic ,
            BoldItalicFont = *-BoldItalic
        ]""",
        "iomc": r"""
        \usepackage{fontspec}
        \setmainfont{Times New Roman}[
            Path=../../../Fonts/,
            UprightFont    = * ,
            BoldFont       = *-Bold ,
            ItalicFont     = *-Italic ,
            BoldItalicFont = *-BoldItalic
        ]""",
        "omics": r"""
        \usepackage{fontspec}
        \setmainfont{Times New Roman}[
            Path=../../../Fonts/,
            UprightFont    = * ,
            BoldFont       = *-Bold ,
            ItalicFont     = *-Italic ,
            BoldItalicFont = *-BoldItalic
        ]""",
    }

    def get_lang_map(self, brand: str = "default") -> dict[str, dict[str, str]]:
        # Return the big lang_map you had earlier.
        # For brevity here we provide just a subset; copy your full map in here.
        lang_map = {
            "default": {
                "polyglossia": r"\setdefaultlanguage{english}",
                "font": LatexLanguageConfig.brand_fonts.get(brand, LatexLanguageConfig.brand_fonts["default"]),
            },
            # === Indic Scripts (Devanagari, Tamil, Bengali, etc.) ===
            "hi": {
                "polyglossia": r"\setdefaultlanguage{hindi}",
                "font": r"\newfontfamily\hindifont{NotoSansDevanagari-Regular.ttf}[Path=../../../Fonts/, Script=Devanagari]",
            },
            "mr": {
                "polyglossia": r"\setdefaultlanguage{marathi}",
                "font": r"\newfontfamily\marathifont{NotoSansDevanagari-Regular.ttf}[Path=../../../Fonts/, Script=Devanagari]",
            },
            "bn": {
                "polyglossia": r"\setdefaultlanguage{bengali}",
                "font": r"\newfontfamily\bengalifont{NotoSansBengali-Regular.ttf}[Path=../../../Fonts/, Script=Bengali]",
            },
            "gu": {
                "polyglossia": r"\setdefaultlanguage{gujarati}",
                "font": r"\newfontfamily\gujaratifont{NotoSansGujarati-Regular.ttf}[Path=../../../Fonts/, Script=Gujarati]",
            },
            "kn": {
                "polyglossia": r"\setdefaultlanguage{kannada}",
                "font": r"\newfontfamily\kannadafont{NotoSansKannada-Regular.ttf}[Path=../../../Fonts/, Script=Kannada]",
            },
            "ta": {
                "polyglossia": r"\setdefaultlanguage{tamil}",
                "font": r"\newfontfamily\tamilfont{NotoSansTamil-Regular.ttf}[Path=../../../Fonts/, Script=Tamil]",
            },
            "te": {
                "polyglossia": r"\setdefaultlanguage{telugu}",
                "font": r"\newfontfamily\telugufont{NotoSansTelugu-Regular.ttf}[Path=../../../Fonts/, Script=Telugu]",
            },
            "ml": {
                "polyglossia": r"\setdefaultlanguage{malayalam}",
                "font": r"\newfontfamily\malayalamfont{NotoSansMalayalam-Regular.ttf}[Path=../../../Fonts/, Script=Malayalam]",
            },
            "or": {
                "polyglossia": r"\setdefaultlanguage{odia}",
                "font": r"\newfontfamily\odiafont{NotoSansOriya-Regular.ttf}[Path=../../../Fonts/, Script=Oriya]",
            },
            "pa": {
                "polyglossia": r"\setdefaultlanguage{punjabi}",
                "font": r"\newfontfamily\punjabifont{NotoSansGurmukhi-Regular.ttf}[Path=../../../Fonts/, Script=Gurmukhi]",
            },
            "ne": {
                "polyglossia": r"\setdefaultlanguage{nepali}",
                "font": r"\newfontfamily\nepalifont{NotoSansDevanagari-Regular.ttf}[Path=../../../Fonts/, Script=Devanagari]",
            },
            "as": {
                "polyglossia": r"\setdefaultlanguage{assamese}",
                "font": r"\newfontfamily\assamesefont{NotoSansBengali-Regular.ttf}[Path=../../../Fonts/, Script=Bengali]",
            },
            "mai": {
                "polyglossia": r"\setdefaultlanguage{maithili}",
                "font": r"\newfontfamily\maithilifont{NotoSansDevanagari-Regular.ttf}[Path=../../../Fonts/, Script=Devanagari]",
            },
            "bho": {
                "polyglossia": r"\setdefaultlanguage{bhojpuri}",
                "font": r"\newfontfamily\bhojpurifont{NotoSansDevanagari-Regular.ttf}[Path=../../../Fonts/, Script=Devanagari]",
            },
            "gom": {
                "polyglossia": r"\setdefaultlanguage{konkani}",
                "font": r"\newfontfamily\konkanifont{NotoSansDevanagari-Regular.ttf}[Path=../../../Fonts/, Script=Devanagari]",
            },
            "sa": {
                "polyglossia": r"\setdefaultlanguage{sanskrit}",
                "font": r"\newfontfamily\sanskritfont{NotoSansDevanagari-Regular.ttf}[Path=../../../Fonts/, Script=Devanagari]",
            },
            "mni-Mtei": {
                "polyglossia": r"\setdefaultlanguage{manipuri}",
                "font": r"\newfontfamily\manipurifont{NotoSansMeeteiMayek-Regular.ttf}[Path=../../../Fonts/]",
            },
            # === Arabic Script (Urdu, Persian, Arabic, Pashto, Sindhi, Kashmiri) ===
            "ur": {
                "polyglossia": r"\setdefaultlanguage{urdu}",
                "font": r"\newfontfamily\urdufont{NotoNastaliqUrdu-Regular.ttf}[Path=../../../Fonts/, Script=Arabic]",
            },
            "ar": {
                "polyglossia": r"\setdefaultlanguage{arabic}",
                "font": r"\newfontfamily\arabicfont{NotoNaskhArabic-Regular.ttf}[Path=../../../Fonts/, Script=Arabic]",
            },
            "fa": {
                "polyglossia": r"\setdefaultlanguage{Persian}",
                "font": r"\setmainfont{NotoNaskhArabic-Regular.ttf}[Path=../../../Fonts/, Script=Arabic]",
            },
            "ps": {
                "polyglossia": r"\setdefaultlanguage{pashto}",
                "font": r"\newfontfamily\pashtofont{NotoNaskhArabic-Regular.ttf}[Path=../../../Fonts/, Script=Arabic]",
            },
            "sd": {
                "polyglossia": r"\setdefaultlanguage{sindhi}",
                "font": r"\newfontfamily\sindhifont{NotoNaskhArabic-Regular.ttf}[Path=../../../Fonts/, Script=Arabic]",
            },
            "ks": {
                "polyglossia": r"\setdefaultlanguage{kashmiri}",
                "font": r"\newfontfamily\kashmirifont{NotoNaskhArabic-Regular.ttf}[Path=../../../Fonts/, Script=Arabic]",
            },
            # === CJK Languages ===
            "zh-CN": {
                "polyglossia": r"\setdefaultlanguage{chinese}",
                "font": r"\newfontfamily\chinesefont{NotoSansSC-Regular.ttf}[Path=../../../Fonts/]",
            },
            "zh-TW": {
                "polyglossia": r"\setdefaultlanguage{chinese}",
                "font": r"\newfontfamily\chinesefont{NotoSansTC-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ja": {
                "polyglossia": r"""\setdefaultlanguage{japanese}
    \XeTeXlinebreaklocale "ja"
    \XeTeXlinebreakskip=0pt plus 1pt""",
                "font": r"""\newfontfamily\japanesefont{NotoSansJP-Regular.ttf}[Path=../../../Fonts/, Script=Kana, Language=Japanese]""",
            },
            "ko": {
                "polyglossia": r"\setdefaultlanguage{korean}",
                "font": r"\newfontfamily\koreanfont{NotoSansKR-Regular.ttf}[Path=../../../Fonts/]",
            },
            # === Other scripts (Amharic, Armenian, Georgian, etc.) ===
            "am": {
                "polyglossia": r"\setdefaultlanguage{amharic}",
                "font": r"\newfontfamily\amharicfont{NotoSansEthiopic-Regular.ttf}[Path=../../../Fonts/, Script=Ethiopic]",
            },
            "hy": {
                "polyglossia": r"\setdefaultlanguage{armenian}",
                "font": r"\newfontfamily\armenianfont{NotoSansArmenian-Regular.ttf}[Path=../../../Fonts/, Script=Armenian]",
            },
            "ka": {
                "polyglossia": r"\setdefaultlanguage{georgian}",
                "font": r"\newfontfamily\georgianfont{NotoSansGeorgian-Regular.ttf}[Path=../../../Fonts/, Script=Georgian]",
            },
            "si": {
                "polyglossia": r"\setdefaultlanguage{sinhala}",
                "font": r"\setmainfont{NotoSansSinhala-Regular.ttf}[Path=../../../Fonts/, Script=Sinhala]",
            },
            "my": {
                "polyglossia": r"\setdefaultlanguage{burmese}",
                "font": r"\newfontfamily\burmesefont{NotoSansMyanmar-Regular.ttf}[Path=../../../Fonts/, Script=Myanmar]",
            },
            "km": {
                "polyglossia": r"\setdefaultlanguage{khmer}",
                "font": r"\newfontfamily\khmerfont{NotoSansKhmer-Regular.ttf}[Path=../../../Fonts/, Script=Khmer]",
            },
            "lo": {
                "polyglossia": r"\setdefaultlanguage{lao}",
                "font": r"\newfontfamily\laofont{NotoSansLao-Regular.ttf}[Path=../../../Fonts/, Script=Lao]",
            },
            "mn": {
                "polyglossia": r"\setdefaultlanguage{mongolian}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/, Script=Cyrillic]",
            },
            "ti": {
                "polyglossia": r"\setdefaultlanguage{tigrinya}",
                "font": r"\newfontfamily\tigrinyafont{NotoSansEthiopic-Regular.ttf}[Path=../../../Fonts/, Script=Ethiopic]",
            },
            # === Latin alphabet languages (Default fallback to NotoSans-Regular) ===
            "af": {
                "polyglossia": r"\setdefaultlanguage{afrikaans}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sq": {
                "polyglossia": r"\setdefaultlanguage{albanian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ay": {
                "polyglossia": r"\setdefaultlanguage{aymara}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "az": {
                "polyglossia": r"\setdefaultlanguage{azerbaijani}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "bm": {
                "polyglossia": r"\setdefaultlanguage{bambara}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "eu": {
                "polyglossia": r"\setdefaultlanguage{basque}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "be": {
                "polyglossia": r"\setdefaultlanguage{belarusian}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "bs": {
                "polyglossia": r"\setdefaultlanguage{bosnian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "bg": {
                "polyglossia": r"\setdefaultlanguage{bulgarian}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ca": {
                "polyglossia": r"\setdefaultlanguage{catalan}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ceb": {
                "polyglossia": r"\setdefaultlanguage{cebuano}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ny": {
                "polyglossia": r"\setdefaultlanguage{chichewa}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "co": {
                "polyglossia": r"\setdefaultlanguage{corsican}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "hr": {
                "polyglossia": r"\setdefaultlanguage{croatian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "cs": {
                "polyglossia": r"\setdefaultlanguage{czech}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "da": {
                "polyglossia": r"\setdefaultlanguage{danish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "dv": {
                "polyglossia": r"\setdefaultlanguage{dhivehi}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "doi": {
                "polyglossia": r"\setdefaultlanguage{dogri}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "nl": {
                "polyglossia": r"\setdefaultlanguage{dutch}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "en": {
                "polyglossia": r"\setdefaultlanguage{english}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "eo": {
                "polyglossia": r"\setdefaultlanguage{esperanto}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "et": {
                "polyglossia": r"\setdefaultlanguage{estonian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ee": {
                "polyglossia": r"\setdefaultlanguage{ewe}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "tl": {
                "polyglossia": r"\setdefaultlanguage{filipino}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "fi": {
                "polyglossia": r"\setdefaultlanguage{finnish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "fr": {
                "polyglossia": r"\setdefaultlanguage{french}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "fy": {
                "polyglossia": r"\setdefaultlanguage{frisian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "gl": {
                "polyglossia": r"\setdefaultlanguage{galician}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "de": {
                "polyglossia": r"\setdefaultlanguage{german}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "el": {
                "polyglossia": r"\setdefaultlanguage{greek}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ht": {
                "polyglossia": r"\setdefaultlanguage{haitian creole}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ha": {
                "polyglossia": r"\setdefaultlanguage{hausa}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "haw": {
                "polyglossia": r"\setdefaultlanguage{hawaiian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "iw": {
                "polyglossia": r"\setdefaultlanguage{hebrew}",
                "font": r"\newfontfamily\hebrewfont{NotoSansHebrew-Regular.ttf}[Path=../../../Fonts/, Script=Hebrew]",
            },
            "hmn": {
                "polyglossia": r"\setdefaultlanguage{hmong}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "hu": {
                "polyglossia": r"\setdefaultlanguage{hungarian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "is": {
                "polyglossia": r"\setdefaultlanguage{icelandic}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ig": {
                "polyglossia": r"\setdefaultlanguage{igbo}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ilo": {
                "polyglossia": r"\setdefaultlanguage{ilocano}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "id": {
                "polyglossia": r"\setdefaultlanguage{indonesian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ga": {
                "polyglossia": r"\setdefaultlanguage{irish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "it": {
                "polyglossia": r"\setdefaultlanguage{italian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "jw": {
                "polyglossia": r"\setdefaultlanguage{javanese}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "kk": {
                "polyglossia": r"\setdefaultlanguage{kazakh}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "rw": {
                "polyglossia": r"\setdefaultlanguage{kinyarwanda}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "kri": {
                "polyglossia": r"\setdefaultlanguage{krio}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ku": {
                "polyglossia": r"\setdefaultlanguage{kurdish (kurmanji)}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ckb": {
                "polyglossia": r"\setdefaultlanguage{kurdish (sorani)}",
                "font": r"\setmainfont{NotoNaskhArabic-Regular.ttf}[Path=../../../Fonts/, Script = Arabic]",
            },
            "ky": {
                "polyglossia": r"\setdefaultlanguage{kyrgyz}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "la": {
                "polyglossia": r"\setdefaultlanguage{latin}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "lv": {
                "polyglossia": r"\setdefaultlanguage{latvian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ln": {
                "polyglossia": r"\setdefaultlanguage{lingala}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "lt": {
                "polyglossia": r"\setdefaultlanguage{lithuanian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "lg": {
                "polyglossia": r"\setdefaultlanguage{luganda}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "lb": {
                "polyglossia": r"\setdefaultlanguage{luxembourgish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "mk": {
                "polyglossia": r"\setdefaultlanguage{macedonian}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/, Script=Cyrillic]",
            },
            "mg": {
                "polyglossia": r"\setdefaultlanguage{malagasy}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ms": {
                "polyglossia": r"\setdefaultlanguage{malay}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "mt": {
                "polyglossia": r"\setdefaultlanguage{maltese}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "mi": {
                "polyglossia": r"\setdefaultlanguage{maori}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "lus": {
                "polyglossia": r"\setdefaultlanguage{mizo}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "no": {
                "polyglossia": r"\setdefaultlanguage{norwegian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "om": {
                "polyglossia": r"\setdefaultlanguage{oromo}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "pl": {
                "polyglossia": r"\setdefaultlanguage{polish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "pt": {
                "polyglossia": r"\setdefaultlanguage{portuguese}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "qu": {
                "polyglossia": r"\setdefaultlanguage{quechua}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ro": {
                "polyglossia": r"\setdefaultlanguage{romanian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ru": {
                "polyglossia": r"\setdefaultlanguage{russian}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sm": {
                "polyglossia": r"\setdefaultlanguage{samoan}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "gd": {
                "polyglossia": r"\setdefaultlanguage{scots gaelic}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "nso": {
                "polyglossia": r"\setdefaultlanguage{sepedi}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sr": {
                "polyglossia": r"\setdefaultlanguage{serbian}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "st": {
                "polyglossia": r"\setdefaultlanguage{sesotho}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sn": {
                "polyglossia": r"\setdefaultlanguage{shona}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sk": {
                "polyglossia": r"\setdefaultlanguage{slovak}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sl": {
                "polyglossia": r"\setdefaultlanguage{slovenian}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "so": {
                "polyglossia": r"\setdefaultlanguage{somali}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "es": {
                "polyglossia": r"\setdefaultlanguage{spanish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "su": {
                "polyglossia": r"\setdefaultlanguage{sundanese}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sw": {
                "polyglossia": r"\setdefaultlanguage{swahili}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "sv": {
                "polyglossia": r"\setdefaultlanguage{swedish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "tg": {
                "polyglossia": r"\setdefaultlanguage{tajik}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "tt": {
                "polyglossia": r"\setdefaultlanguage{tatar}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "th": {
                "polyglossia": r"""\setdefaultlanguage{thai}\XeTeXlinebreaklocale "th" \XeTeXlinebreakskip = 0pt plus 1pt""",
                "font": r"""\newfontfamily\thaifont{NotoSansThai-Regular.ttf}[Path=../../../Fonts/, Script=Thai]""",
            },
            "ts": {
                "polyglossia": r"\setdefaultlanguage{tsonga}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "tr": {
                "polyglossia": r"\setdefaultlanguage{turkish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "tk": {
                "polyglossia": r"\setdefaultlanguage{turkmen}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ak": {
                "polyglossia": r"\setdefaultlanguage{twi}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "uk": {
                "polyglossia": r"\setdefaultlanguage{ukrainian}",
                "font": r"\setmainfont{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "ug": {
                "polyglossia": r"\setdefaultlanguage{uyghur}",
                "font": r"\newfontfamily\uyghurfont{NotoNaskhArabic-Regular.ttf}[Path=../../../Fonts/, Script=Arabic]",
            },
            "uz": {
                "polyglossia": r"\setdefaultlanguage{uzbek}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "vi": {
                "polyglossia": r"\setdefaultlanguage{vietnamese}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "cy": {
                "polyglossia": r"\setdefaultlanguage{welsh}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "xh": {
                "polyglossia": r"\setdefaultlanguage{xhosa}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "yi": {
                "polyglossia": r"\setdefaultlanguage{yiddish}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "yo": {
                "polyglossia": r"\setdefaultlanguage{yoruba}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
            "zu": {
                "polyglossia": r"\setdefaultlanguage{zulu}",
                "font": r"\newfontfamily\notosans{NotoSans-Regular.ttf}[Path=../../../Fonts/]",
            },
        }
        return lang_map


# convenience helper to keep old import style `from Apps.language_fonts import get_lang_map`
def get_lang_map(brand: str = "default"):
    return LatexLanguageConfig().get_lang_map(brand)


__all__ = ["LatexLanguageConfig", "get_lang_map"]
