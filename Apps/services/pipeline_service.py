from Apps.config import Config
from Apps.services.io_service import IOService
from Apps.models_journal import PulsusInputStr, PulsusOutputStr
from Apps.language_fonts import LatexLanguageConfig
from Apps.library_import import *
from Apps.library_import import pathOfPathLib


class PipelineService:
    """
    Handles the complete pipeline for journal processing and PDF generation.
    """

    gemClient, GroqClient, CORE_API_KEY = Config.init_clients()

    @staticmethod
    async def process_journal(journal: PulsusInputStr):
        """
        Full journal pipeline:
        1. Save input
        2. Generate content using Gemini
        3. Parse + clean content
        4. Generate PDF & HTML
        5. Return JSON status
        """
        # ---------- Step 1: Store input ----------
        data = IOService.fetchInputData()
        journal.id = journal.id.strip()
        if journal.id in data:
            raise HTTPException(status_code=400, detail="Journal ID already exists.")
        data[journal.id] = journal.model_dump(exclude=["id"])
        print("Step 1 : Save journal input ✅")

        # ---------- Step 2: Build LLM Prompt ----------
        prompt = PipelineService._build_prompt(journal)
        print("Step 2 : Created universal prompt ✅")

        # ---------- Step 3: Ask Gemini ----------
        # gem_summary = PipelineService._ask_gemini_with_retries(prompt)
        # print("Step 3 : Gemini response received ✅")

        # ---------- Step 3,4: Meta data Parse LLM JSON ----------
        content_data = PipelineService._parse_gemini_response(prompt)
        print("Step 3,4 : Generation with Parsing the structured JSON ✅")

        # ---------- Step 5: Create title, abstract, summary ----------
        processed_sections = PipelineService._process_sections(content_data)
        processed_sections = PipelineService._normalize_content_structure(
            processed_sections
        )
        print("Step 5 : Generated summary/introduction/description ✅")

        gem_title = PipelineService._generate_title(
            processed_sections["content"]["summary"], journal
        )
        print("Step 6 : Generated title ✅")

        # ---------- Step 6: Save structured data ----------
        final_output = PipelineService._build_final_output(
            journal, gem_title, content_data, processed_sections["content"]
        )

        IOService.saveInputData(data)
        output_data = IOService.fetchOutputData()
        pulsus_output_instance = PulsusOutputStr(**final_output[journal.id])
        output_data[journal.id] = pulsus_output_instance.model_dump()
        IOService.saveOutputData(output_data)
        print("Step 7 : Saved output data ✅")

        # ---------- Step 7: Generate files ----------
        PipelineService._generate_html_and_pdf(journal, output_data)
        print("Step 8 : Generated HTML and PDF ✅")

        # ---------- Step 8: Return success ----------
        return JSONResponse(
            status_code=200,
            content={
                "Status": f"Data added and files generated successfully in PDFStorePulsus/{journal.id}/ ✅."
            },
        )

    # =====================================================================================================================================
    # Internal helper methods
    # =====================================================================================================================================

    @staticmethod
    def _build_prompt(journal: PulsusInputStr) -> str:
        return f"""
        You are provided by a topic:
        topic : "{journal.topic}"
        ...
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
            ...
        """

    @staticmethod
    def _ask_gemini_with_retries(prompt: str, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                response = PipelineService.gemClient.models.generate_content(
                    model="gemini-2.5-pro", contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"Gemini attempt {attempt + 1} failed: {e}")
                time.sleep(3)
                if attempt == retries - 1:
                    raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def _parse_gemini_response(prompt: str, retries: int = 3) -> dict:
        """
        Generate Gemini response and parse JSON.
        If parsing fails, retry up to `retries` times by regenerating Gemini output.
        """
        attempt = 0
        while attempt < retries:
            gem_response = PipelineService._ask_gemini_with_retries(prompt)

            try:
                raw_json = IOService.extract_json_from_markdown(gem_response)
                parsed = json.loads(raw_json)

            except json.JSONDecodeError as e:
                attempt += 1
                print(f"JSON parsing failed (attempt {attempt}/{retries}): {e}")
                if attempt >= retries:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to parse Gemini JSON after {retries} attempts: {e}",
                    )
                print("Retrying Gemini generation...")
                time.sleep(2)
                continue
            return parsed

    @staticmethod
    def _normalize_content_structure(parsed_json: dict) -> dict:
        """
        Normalize Gemini response structure.
        Ensures the output always follows:
        {"content": {...}} format.
        """
        if "content" in parsed_json:
            return parsed_json  # already correct format

        # If flat, wrap it inside 'content'
        return {"content": parsed_json}

    @staticmethod
    def _process_sections(content_data: dict) -> dict:
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

        parsed = PipelineService._parse_gemini_response(prompt)
        normalized = PipelineService._normalize_content_structure(parsed)
        return normalized

    @staticmethod
    def _generate_title(summary: str, journal: PulsusInputStr) -> str:
        """Generate title via Gemini."""
        prompt = f"""
        Generate a 5-7 word title based on this summary: {summary}
        
        IMPORTANT: Respond with ONLY the title. No additional text, explanations, or formatting.
        """
        response = PipelineService._ask_gemini_with_retries(prompt)

        if journal.brandName == "alliedAcademy.tex":
            storeTempTitle = response.split(": ")
            if len(storeTempTitle) != 1:
                count = 0
                for i in storeTempTitle:
                    storeTempTitle[count] = i.capitalize()
                    count += 1
                response = ": ".join(storeTempTitle)
            else:
                response = response.capitalize()
            storeTempTitle = None

        return response.strip()

    @staticmethod
    def _build_final_output(journal, gem_title, content_data, gem_info):
        """Combine all data into one dict."""
        return {
            journal.id: {
                "title": gem_title,
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
                "content": content_data.get("content", {}),
                "doi": journal.doi,
                "received": journal.received,
                "editorAssigned": journal.editorAssigned,
                "reviewed": journal.reviewed,
                "revised": journal.revised,
                "published": journal.published,
                "year": int(journal.published.split("-")[-1]),
                "manuscriptNo": journal.manuscriptNo,
                "QCNo": (
                    f"Q-{journal.manuscriptNo.split('-')[-1]}"
                    if journal.brandName == "hilaris.tex"
                    else journal.manuscriptNo
                ),
                "preQCNo": (
                    f"P-{journal.manuscriptNo.split('-')[-1]}"
                    if journal.brandName == "hilaris.tex"
                    else journal.manuscriptNo
                ),
                "RManuNo": (
                    f"R-{journal.manuscriptNo.split('-')[-1]}"
                    if journal.brandName == "hilaris.tex"
                    else journal.manuscriptNo
                ),
                "volume": (
                    f"0{journal.volume}"
                    if len(str(journal.volume)) == 1
                    else str(journal.volume)
                ),
                "issues": (
                    f"0{journal.issues}"
                    if len(str(journal.issues)) == 1
                    else str(journal.issues)
                ),
                "pdfNo": journal.pdfNo,
                "ISSN": journal.ISSN,
                "imgPath": journal.imgPath,
                "parentLink": str(journal.parentLink),
                "conclusion": gem_info["summary"],
            }
        }

    @staticmethod
    def _generate_html_and_pdf(journal, output_data):
        """Move all your LaTeX + HTML rendering logic here."""
        # --- Centralized Directory Setup ---

        # Create a single directory for all of this journal's output files.
        output_base_dir = pathOfPathLib("Apps/DB/PDFStorePulsus")
        journal_folder = output_base_dir/journal.id
        journal_folder.mkdir(parents=True, exist_ok=True)

        print("Step 8.1 : Final response ✅")

        # --- 9: Create HTML file ---
        env_html = Environment(
            loader=FileSystemLoader(pathOfPathLib("Apps/templates/"))
        )
        try:
            html_template = env_html.get_template("Format.html")
            forHtml = copy.deepcopy(output_data[journal.id])

            # Logic for processing references for HTML

            for i in range(1, len(forHtml["content"]) + 1):
                forHtml["introduction"] = forHtml["introduction"].replace(
                    f"[{i}].", f"[<a href='#{i}' title='{i}'>{i}</a>].</p><p>"
                )

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

                if journal.brandName == "alliedAcademy.tex":
                    temp = f"""<p><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>. {i["journalShortName"]}. {i["published"]};{i["volume"]}{i["issues"]}:{i["pageRangeOrNumber"]}.</li>
                    <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
                elif journal.brandName == "omics.tex":
                    temp = f"""<li><a name="{count}" id="{count}"></a>{i["authors"]} ({i["published"]}) <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>.{i["journalShortName"]} {i["volume"]}:{i["pageRangeOrNumber"]}.</li>
                    <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
                elif journal.brandName == "hilaris.tex":
                    temp = f"""<li><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">"{i["title"]}"</a>.<i>{i["journalShortName"]}</i> {i["volume"]} ({i["published"]}):{i["pageRangeOrNumber"]}.</li>
                    <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""
                else:
                    temp = f"""<p><a name="{count}" id="{count}"></a>{i["authors"]}. <a href="{i["parentLink"]}" target="_blank">{i["title"]}</a>. {i["journalShortName"]}. {i["published"]};{i["volume"]}{i["issues"]}:{i["pageRangeOrNumber"]}.</p>
                    <p align="right"><a href="{i["url"]}" target="_blank"><u>Indexed at</u></a>, <a href="https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={'+'.join(i["title"].split(' '))}&btnG=" target="_blank"><u>Google Scholar</u></a>, <a href="https://doi.org/{i["DOI"]}" target="_blank"><u>Crossref</u></a></p>"""

                forHtml["storeRefPart"] = f"""{forHtml['storeRefPart']}\n{temp}"""

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

            # Save the HTML file inside the journal's dedicated folder
            html_file_path = journal_folder / f"{journal.id}.html"
            html_file_path.write_text(rendered_html, encoding="utf-8")

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to generate HTML file: {str(e)}"
            )

        print("Step 9 : Created HTML file ✅")

        # --- 10: Create PDF file ---
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
            loader=FileSystemLoader(pathOfPathLib("Apps/templates")),
        )

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

            # First escape LaTeX
            ref = latex_escape(ref)

            # Regex: Find journal short name (before year/volume/semicolon/parenthesis)
            # Example match: " J. Biomol. Struct. Dyn"
            pattern = r"(\s)([A-Z][A-Za-z\.\s]+)(?=\s\d|\s\(|;)"

            def repl(match):
                return f" \\textit{{{match.group(2).strip()}}}"

            return re.sub(pattern, repl, ref, count=1)

        env_latex.filters["latex_escape"] = latex_escape
        env_latex.filters["format_reference"] = format_reference
        template = env_latex.get_template(journal.brandName)

        brand_key = journal.brandName.replace(".tex", "")
        lang_map = LatexLanguageConfig.get_lang_map(brand_key)

        # --- ensure initial PDF has an English preamble and mark language in saved record ---
        default_cfg = lang_map.get("default")

        # Build preamble: polyglossia + the font block stored in default_cfg
        preamble = (
            "\\usepackage{polyglossia}\n"
            + default_cfg["polyglossia"]
            + "\n"
            + default_cfg["font"]
        )
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
                cwd=journal_folder,  # CRITICAL: Set the working directory
            )

            if result.returncode != 0:
                log_file_path = tex_file_path.with_suffix(".log")

                # The log file is already saved by xelatex, so we just read it for the error message
                error_text = "Unknown LaTeX error. Check the log file."
                if log_file_path.exists():
                    with open(log_file_path, "r") as f:
                        lines = f.readlines()
                    error_snippets = [line for line in lines if line.startswith("! ")]
                    error_text = (
                        "\n".join(error_snippets)
                        or f"LaTeX compilation failed. Full log in {log_file_path}"
                    )

                raise HTTPException(
                    status_code=500,
                    detail=f"LaTeX compilation failed on run {i + 1}:\n\n{error_text}",
                )

        print("Step 10 : Create PDF file ✅")

        return JSONResponse(
            status_code=200,
            content={
                "Status": f"Data added and files generated successfully in PDFStorePulsus/{journal.id}/ ✅."
            },
        )
