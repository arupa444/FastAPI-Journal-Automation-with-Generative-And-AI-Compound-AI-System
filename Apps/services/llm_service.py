from Apps.config import Config
from Apps.library_import import HTTPException, httpx
from Apps.models_journal import ArticleItem

class LLMService:

    gem_client, groq_client, CORE_API_KEY = Config.init_clients()
    CORE_API_URL = "https://api.core.ac.uk/v3/search/works"

    @staticmethod
    def process_gemini(prompt: str) -> str:
        """Send prompt to Gemini and return model response."""
        try:
            response = LLMService.gem_client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return getattr(response, "text", str(response))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

    @staticmethod
    def process_groq(prompt: str) -> str:
        """Send prompt to Groq API and return model response."""
        try:
            response = LLMService.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")

    @staticmethod
    async def process_core_search(prompt: str) -> dict:
        """Fetch scholarly articles from CORE API and structure results."""
        headers = {
            "Authorization": f"Bearer {LLMService.CORE_API_KEY}",
            "Content-Type": "application/json",
        }
        data = {"q": prompt, "limit": 20}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    LLMService.CORE_API_URL, json=data, headers=headers
                )
                response.raise_for_status()
                results = response.json()
                return LLMService._build_structured_content(results)

        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"CORE API returned HTTP error: {e.response.text}",
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    @staticmethod
    def _build_structured_content(results):
        """Format CORE API results into a structured content dict."""
        content = {}
        for idx, item in enumerate(results.get("results", []), start=1):
            key = f"C{str(idx).zfill(3)}"

            title = item.get("title", "No title available")
            abstract = item.get("abstract", "No abstract available.")
            authors = (
                ", ".join([a.get("name", "Unknown") for a in item.get("authors", [])])
                or "Unknown author(s)"
            )
            published_date = item.get("published", "Unknown date")
            doi = item.get("doi", "DOI not available")
            url = item.get("url", "https://URLNotAvailable")
            fulltext_links = item.get("fulltextUrls", [])
            subjects = (
                ", ".join(item.get("topics", []))
                if item.get("topics")
                else "No keywords"
            )
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
                "references": references,
            }

            temp_item = ArticleItem(**content[key])
            content[key] = temp_item.model_dump()

        return {"content": content}
