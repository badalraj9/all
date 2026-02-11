import os
import asyncio
import time
from typing import List, Dict, Optional
import requests
# Placeholder for 'arxiv' library if not installed, assuming standard behavior or simplified fetch

class ResearchEngine:
    """
    JARVIS Research Engine (Assimilated ORE).
    """
    def __init__(self, download_dir: str = "/tmp/jarvis_research"):
        self.download_dir = download_dir
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Simplified ArXiv search without external dependency if possible,
        or assuming `arxiv` package is available in environment.
        For assimilation, we use the logic from ORE.
        """
        try:
            import arxiv
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            results = []
            for r in client.results(search):
                results.append({
                    "title": r.title,
                    "authors": [a.name for a in r.authors],
                    "abstract": r.summary,
                    "url": r.entry_id,
                    "pdf_url": r.pdf_url,
                    "published": str(r.published)
                })
            return results
        except ImportError:
            return [{"error": "ArXiv library not installed."}]
        except Exception as e:
            return [{"error": str(e)}]

    async def fetch_paper(self, pdf_url: str) -> Optional[str]:
        """
        Downloads a paper to the local cache.
        """
        filename = pdf_url.split('/')[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        filepath = os.path.join(self.download_dir, filename)

        if os.path.exists(filepath):
            return filepath

        try:
            response = requests.get(pdf_url)
            if response.status_code == 200:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                return filepath
        except Exception as e:
            print(f"Failed to download: {e}")
        return None
