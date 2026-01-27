import asyncio
import feedparser
import spacy
from typing import Dict, Any, List
from urllib.parse import quote_plus
from JARVIS.plugins.base_plugin import BasePlugin
from JARVIS.core.event_bus import event_bus, Event, EventPriority
from loguru import logger

class ResearchPlugin(BasePlugin):
    async def initialize(self, context: Dict[str, Any]):
        self.nlp = spacy.load("en_core_web_sm")
        event_bus.subscribe("research.start", self.handle_research_request)
        logger.info("ORE Research Plugin initialized (Real Mode).")

    async def cleanup(self):
        pass

    async def handle_research_request(self, event: Event):
        query = event.data.get("query")
        logger.info(f"ORE: Fetching real ArXiv papers for '{query}'...")

        # 1. Fetch from ArXiv
        papers = await self._fetch_arxiv(query)

        if not papers:
            logger.warning(f"ORE: No papers found for {query}")
            await event_bus.emit("task.fail", {"reason": "No papers found"}, source="research_ore")
            return

        # 2. Analyze the first paper
        top_paper = papers[0]
        analysis = self._analyze_text(top_paper['summary'])

        findings = {
            "title": top_paper['title'],
            "source": top_paper['link'],
            "summary": top_paper['summary'][:500] + "...",
            "entities": analysis['entities'],
            "key_phrases": analysis['noun_chunks']
        }

        logger.info(f"ORE: Analysis complete. Found: {findings['title']}")

        # 3. Emit Result
        await event_bus.emit(
            "research.complete",
            {"query": query, "findings": findings},
            source="research_ore"
        )

        # 4. Ingest into Memory
        await event_bus.emit(
            "memory.ingest",
            {
                "actor": "ORE",
                "action": "OBSERVE",
                "object_id": str(hash(findings['title'])),
                "payload": findings,
                "truth_vector": {
                    "confidence": 0.9,
                    "authority": 0.8, # ArXiv is authoritative
                    "freshness": 1.0
                }
            },
            source="research_ore",
            priority=EventPriority.HIGH
        )

    async def _fetch_arxiv(self, query: str, max_results=3) -> List[Dict]:
        """Fetch papers from ArXiv API."""
        encoded_query = quote_plus(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}"

        # Run synchronous feedparser in thread
        feed = await asyncio.to_thread(feedparser.parse, url)

        results = []
        for entry in feed.entries:
            results.append({
                "title": entry.title,
                "summary": entry.summary,
                "link": entry.link,
                "published": entry.published
            })
        return results

    def _analyze_text(self, text: str) -> Dict[str, Any]:
        """Extract entities and noun chunks using Spacy."""
        doc = self.nlp(text)
        return {
            "entities": [ent.text for ent in doc.ents],
            "noun_chunks": [chunk.text for chunk in doc.noun_chunks]
        }
