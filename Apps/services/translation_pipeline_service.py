from Apps.library_import import *
from Apps.library_import import pathOfPathLib
from Apps.services.io_service import IOService
from Apps.services.translate_service import TranslationService
from Apps.language_fonts import LatexLanguageConfig
from Apps.models_journal import TranslatePage


class TranslationPipelineService:
    """
    Handles translation of journal outputs (PDF + HTML) into target language.
    """

    @staticmethod
    async def translate_journal(translatePage: TranslatePage):
        print("Start the process of translation ✅")

        output_data = IOService.fetch_output_data()
        if translatePage.id not in output_data:
            details = "Journal ID doesn't exist. Available IDs:"
            details += " ".join(output_data.keys())
            raise HTTPException(status_code=404, detail=details)

        journal_data = output_data[translatePage.id]

        # -------- Step 1: Translation --------
        tempStore = {
            "introduction": journal_data["introduction"],
            "description": journal_data["description"],
            "abstract": journal_data["abstract"],
            "keywords": journal_data["keywords"],
            "conclusion": journal_data["conclusion"],
        }

        print("Step 1: Start Translation ✅")
        translated = TranslationService.translate_dict(tempStore, translatePage.language)

        for key, value in translated.items():
            journal_data[key] = value

        # -------- Step 2: Directory Setup --------
        output_base_dir = pathOfPathLib("Apps/DB/PDFTranslatedStorePulsus")
        journal_folder = (
            output_base_dir / f"{translatePage.language}_translate_{translatePage.id}"
        )
        journal_folder.mkdir(parents=True, exist_ok=True)
        print("Step 2: Folder ready ✅")

        # -------- Step 3: HTML Generation --------
        TranslationPipelineService._generate_html(
            journal_data, journal_folder, translatePage
        )
        print("Step 3: Created HTML ✅")

        # -------- Step 4: PDF Generation --------
        TranslationPipelineService._generate_pdf(
            journal_data, journal_folder, translatePage, output_data
        )
        print("Step 4: Created PDF ✅")

        # -------- Step 5: Done --------
        return JSONResponse(
            status_code=200,
            content={
                "Status": f"Translated files generated successfully in PDFTranslatedStorePulsus/{translatePage.id}/ ✅"
            },
        )

    # ------------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------------

    @staticmethod
    def _generate_html(journal_data, journal_folder, translatePage: TranslatePage):
        env_html = Environment(loader=FileSystemLoader(pathOfPathLib("Apps/templates/")))
        html_template = env_html.get_template("Format1.html")
        forHtml = copy.deepcopy(journal_data)

        # Replace references
        for i in range(1, len(forHtml["content"]) + 1):
            forHtml["introduction"] = forHtml["introduction"].replace(
                f"[{i}].", f"[<a href='#{i}' title='{i}'>{i}</a>].</p><p>"
            )
            forHtml["description"] = forHtml["description"].replace(
                f"[{i}].", f"[<a href='#{i}' title='{i}'>{i}</a>]."
            )

        forHtml["description"] = forHtml["description"].replace("\n\n", "</p><p>")
        forHtml["description"] = forHtml["description"].replace("\n", "</p><p>")

        # Store body sections depending on brand
        brand = journal_data["brandName"]
        storeBody = TranslationPipelineService._build_store_body(brand, forHtml)
        forHtml["storeBody"] = storeBody

        # Build references HTML
        forHtml["storeRefPart"] = TranslationPipelineService._build_html_references(
            brand, forHtml
        )

        # Handle author department lines
        department_parts = forHtml["authorsDepartment"].split(",")
        if len(department_parts) > 1:
            forHtml["prefixAuthorDepartment"] = f"{department_parts[0]}<br />"
            forHtml["suffixAuthorDepartment"] = (
                f"{','.join(department_parts[1:])}.<br />"
            )
        else:
            forHtml["prefixAuthorDepartment"] = forHtml["authorsDepartment"]
            forHtml["suffixAuthorDepartment"] = "<br />"

        rendered_html = html_template.render(**forHtml)
        html_file_path = journal_folder / f"{translatePage.id}.html"
        html_file_path.write_text(rendered_html, encoding="utf-8")

    @staticmethod
    def _build_store_body(brand, forHtml):
        body = {}
        if brand == "alliedAcademy.tex":
            body["Introduction"] = forHtml["introduction"]
            body["Conclusion"] = forHtml["conclusion"]
        elif brand == "omics.tex":
            body.update(
                {
                    "Abstract": forHtml["abstract"],
                    "Keywords": forHtml["keywords"],
                    "Introduction": forHtml["introduction"],
                    "Description": forHtml["description"],
                    "Conclusion": forHtml["conclusion"],
                }
            )
        elif brand == "hilaris.tex":
            body.update(
                {
                    "Introduction": forHtml["introduction"],
                    "Description": forHtml["description"],
                    "Conclusion": forHtml["conclusion"],
                    "Acknowledgement": None,
                    "Conflict_of_Interest": None,
                }
            )
        else:
            body.update(
                {
                    "Introduction": forHtml["introduction"],
                    "Description": forHtml["description"],
                    "Conclusion": forHtml["conclusion"],
                }
            )
        return body

    @staticmethod
    def _build_html_references(brand, forHtml):
        ref_html = ""
        count = 0
        for item in forHtml["content"].values():
            count += 1
            item["issues"] = f"({item['issues']})" if item.get("issues") else ""
            base_ref = (
                f"<li><i><a name='{count}' id='{count}'></a>{item['authors']}. "
                f"<a href='{item['parentLink']}' target='_blank'>{item['title']}</a>. "
                f"{item['journalShortName']}. {item['published']};{item['volume']}{item['issues']}:{item['pageRangeOrNumber']}.</i></li>"
            )
            scholar_links = (
                f"<p align='right'><a href='{item['url']}' target='_blank'><u>Indexed at</u></a>, "
                f"<a href='https://scholar.google.com/scholar?hl=en&q={'+'.join(item['title'].split(' '))}' target='_blank'><u>Google Scholar</u></a>, "
                f"<a href='https://doi.org/{item['DOI']}' target='_blank'><u>Crossref</u></a></p>"
            )
            ref_html += f"{base_ref}\n{scholar_links}"
        return ref_html

    @staticmethod
    def _generate_pdf(journal_data, journal_folder, translatePage, output_data):
        env_latex = Environment(
            block_start_string=r"\BLOCK{",
            block_end_string="}",
            variable_start_string=r"\VAR{",
            variable_end_string="}",
            comment_start_string=r"\#{",
            comment_end_string="}",
            line_statement_prefix="%%",
            line_comment_prefix="%#",
            trim_blocks=True,
            autoescape=False,
            loader=FileSystemLoader(pathOfPathLib("./templates")),
        )

        # Escape + reference formatting filters
        def latex_escape(text):
            if not isinstance(text, str):
                return text
            replacements = {
                "&": r"\&",
                "%": r"\%",
                "$": r"\$",
                "#": r"\#",
                "_": r"\_",
                "{": r"\{",
                "}": r"\}",
                "^": r"\^{}",
                "~": r"\textasciitilde{}",
                "\\": r"\textbackslash{}",
            }
            pattern = re.compile("|".join(re.escape(k) for k in replacements.keys()))
            return pattern.sub(lambda m: replacements[m.group()], text)

        def format_reference(ref: str) -> str:
            if not isinstance(ref, str):
                return ref
            ref = latex_escape(ref)
            pattern = r"(\s)([A-Z][A-Za-z\.\s]+)(?=\s\d|\s\(|;)"

            def repl(match):
                return f" \\textit{{{match.group(2).strip()}}}"

            return re.sub(pattern, repl, ref, count=1)

        env_latex.filters["latex_escape"] = latex_escape
        env_latex.filters["format_reference"] = format_reference
        template = env_latex.get_template(journal_data["brandName"])

        # Determine language setup
        brand_key = journal_data["brandName"].replace(".tex", "")
        lang_map = LatexLanguageConfig.get_lang_map(brand_key)

        target_lang = translatePage.language or output_data[translatePage.id].get(
            "lang", "en"
        )
        lang_config = lang_map.get(target_lang, lang_map["default"])

        match = re.search(r"\{(.*?)\}", lang_config.get("polyglossia", ""))
        lang_name = match.group(1) if match else target_lang

        if target_lang in ("default", "en", "english"):
            preamble = (
                "\\usepackage{polyglossia}\n"
                + r"\setdefaultlanguage{english}\n"
                + lang_map["default"]["font"]
            )
        else:
            preamble = (
                "\\usepackage{polyglossia}\n"
                + f"\\setdefaultlanguage{{{lang_name}}}\n"
                + lang_config["font"]
            )

        output_data[translatePage.id]["preamble"] = preamble
        output_data[translatePage.id]["lang_name"] = lang_name
        output_data[translatePage.id]["lang"] = target_lang

        rendered_latex = template.render(**output_data[translatePage.id])
        tex_file_path = journal_folder / f"{translatePage.id}.tex"
        tex_file_path.write_text(rendered_latex, encoding="utf-8")

        # Compile to PDF
        for i in range(2):
            result = subprocess.run(
                ["xelatex", "-interaction=nonstopmode", tex_file_path.name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=journal_folder,
            )
            if result.returncode != 0:
                log_path = tex_file_path.with_suffix(".log")
                error_text = "LaTeX compilation failed."
                if log_path.exists():
                    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                        errors = [line for line in f if line.startswith("! ")]
                    error_text = "\n".join(errors) or f"Full log in {log_path}"
                raise HTTPException(status_code=500, detail=error_text)
