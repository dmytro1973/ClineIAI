import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import re
from bs4 import BeautifulSoup
import httpx

from .base import BaseScraper, ScraperConfig, SearchResult, DocumentMetadata
from ..models.document import Document

# Configure logging
logger = logging.getLogger(__name__)

class AWMFScraper(BaseScraper):
    """Scraper for AWMF S3 guidelines"""

    def __init__(self, config: Optional[ScraperConfig] = None):
        super().__init__(config or ScraperConfig(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            timeout=30,
            max_retries=3,
            retry_delay=1.0,
            rate_limit=30,  # 30 requests per minute
            concurrent_requests=3,
            cache_enabled=True,
            cache_ttl=3600
        ))

    @property
    def source(self) -> str:
        return "awmf"

    @property
    def source_name(self) -> str:
        return "AWMF S3-Leitlinien"

    @property
    def base_url(self) -> str:
        return "https://www.awmf.org"

    @property
    def requires_authentication(self) -> bool:
        return False

    async def _extract_search_results(self, soup: BeautifulSoup) -> List[SearchResult]:
        """Extract search results from AWMF search page"""
        results = []

        # Find guideline entries - this needs to be adjusted based on actual AWMF website structure
        guideline_entries = soup.select("div.guideline-entry") or []

        for entry in guideline_entries:
            try:
                title_elem = entry.select_one("h3 a")
                if not title_elem:
                    continue

                title = title_elem.text.strip()
                url = title_elem["href"]
                if not url.startswith("http"):
                    url = f"{self.base_url}{url}"

                # Extract source ID from URL
                source_id = self._generate_document_id(url)

                # Extract additional metadata
                authors = []
                published_date = None
                abstract = None
                keywords = []

                # Extract authors if available
                author_elem = entry.select_one("div.authors")
                if author_elem:
                    authors = [a.text.strip() for a in author_elem.select("span.author")]

                # Extract date if available
                date_elem = entry.select_one("div.date")
                if date_elem:
                    try:
                        published_date = datetime.strptime(date_elem.text.strip(), "%d.%m.%Y")
                    except ValueError:
                        published_date = None

                # Extract abstract if available
                abstract_elem = entry.select_one("div.abstract")
                if abstract_elem:
                    abstract = abstract_elem.text.strip()

                # Extract keywords if available
                keyword_elem = entry.select_one("div.keywords")
                if keyword_elem:
                    keywords = [kw.text.strip() for kw in keyword_elem.select("span.keyword")]

                # Extract file URL if available
                file_url = None
                file_elem = entry.select_one("a.download")
                if file_elem and "href" in file_elem.attrs:
                    file_url = file_elem["href"]
                    if not file_url.startswith("http"):
                        file_url = f"{self.base_url}{file_url}"

                results.append(SearchResult(
                    title=title,
                    url=url,
                    source=self.source,
                    source_id=source_id,
                    authors=authors if authors else None,
                    published_date=published_date,
                    abstract=abstract,
                    keywords=keywords if keywords else None,
                    file_url=file_url,
                    raw_data={"html": str(entry)}
                ))

            except Exception as e:
                logger.error(f"Error parsing guideline entry: {str(e)}")
                continue

        return results

    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search AWMF guidelines"""
        try:
            # Construct search URL - this needs to be adjusted based on actual AWMF search URL structure
            search_url = f"{self.base_url}/leitlinien/aktuelle-leitlinien.html"

            # Add query parameters if needed
            params = {"q": query} if query else None

            response = await self._get_with_retry(search_url, params)
            soup = self._parse_html(response.text)

            results = await self._extract_search_results(soup)

            # Limit results
            return results[:max_results]

        except Exception as e:
            logger.error(f"Error searching AWMF guidelines: {str(e)}")
            raise

    async def _extract_document_metadata(self, soup: BeautifulSoup, url: str) -> DocumentMetadata:
        """Extract detailed metadata from guideline page"""
        # Extract title
        title_elem = soup.select_one("h1")
        title = title_elem.text.strip() if title_elem else "Unknown Title"

        # Extract authors
        authors = []
        author_elements = soup.select("div.authors span.author")
        for author_elem in author_elements:
            authors.append(author_elem.text.strip())

        # Extract published date
        published_date = None
        date_elem = soup.select_one("div.published-date")
        if date_elem:
            try:
                published_date = datetime.strptime(date_elem.text.strip(), "%d.%m.%Y")
            except ValueError:
                published_date = None

        # Extract publisher
        publisher = "AWMF"

        # Extract DOI if available
        doi = None
        doi_elem = soup.select_one("meta[name='citation_doi']")
        if doi_elem and "content" in doi_elem.attrs:
            doi = doi_elem["content"]

        # Extract language
        language = "de"  # AWMF guidelines are typically in German

        # Extract keywords
        keywords = []
        keyword_elements = soup.select("div.keywords span.keyword")
        for keyword_elem in keyword_elements:
            keywords.append(keyword_elem.text.strip())

        # Extract abstract
        abstract = None
        abstract_elem = soup.select_one("div.abstract")
        if abstract_elem:
            abstract = abstract_elem.text.strip()

        return DocumentMetadata(
            title=title,
            authors=authors if authors else None,
            published_date=published_date,
            publisher=publisher,
            doi=doi,
            language=language,
            keywords=keywords if keywords else None,
            abstract=abstract
        )

    async def get_document_details(self, source_id: str) -> DocumentMetadata:
        """Get detailed metadata for a specific guideline"""
        try:
            # This is a simplified implementation - in reality, you would need to:
            # 1. Parse the source_id to get the actual URL or ID
            # 2. Fetch the specific guideline page
            # 3. Extract detailed metadata

            # For now, we'll return a mock response
            return DocumentMetadata(
                title=f"AWMF Guideline {source_id}",
                authors=["AWMF"],
                published_date=datetime.now(),
                publisher="AWMF",
                language="de",
                abstract="This is a placeholder abstract for the AWMF guideline."
            )

        except Exception as e:
            logger.error(f"Error getting document details for {source_id}: {str(e)}")
            raise

    async def download_document(self, source_id: str, output_path: str) -> bool:
        """Download guideline document"""
        try:
            # This is a simplified implementation - in reality, you would need to:
            # 1. Parse the source_id to get the download URL
            # 2. Fetch the document (PDF)
            # 3. Save it to the specified output path

            # For now, we'll simulate a successful download
            logger.info(f"Simulating download of {source_id} to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error downloading document {source_id}: {str(e)}")
            return False

    async def get_guideline_categories(self) -> List[Dict[str, Any]]:
        """Get available guideline categories"""
        try:
            # Fetch the main guidelines page
            url = f"{self.base_url}/leitlinien/aktuelle-leitlinien.html"
            response = await self._get_with_retry(url)
            soup = self._parse_html(response.text)

            # Extract categories - this needs to be adjusted based on actual AWMF structure
            categories = []
            category_elements = soup.select("div.category")

            for elem in category_elements:
                name_elem = elem.select_one("h2")
                if name_elem:
                    categories.append({
                        "name": name_elem.text.strip(),
                        "count": len(elem.select("div.guideline-entry")),
                        "url": f"{self.base_url}{name_elem.find_parent('a')['href']}" if name_elem.find_parent('a') else None
                    })

            return categories

        except Exception as e:
            logger.error(f"Error getting guideline categories: {str(e)}")
            return []

    async def get_recent_guidelines(self, limit: int = 10) -> List[SearchResult]:
        """Get recently published guidelines"""
        try:
            # Fetch the main guidelines page
            url = f"{self.base_url}/leitlinien/aktuelle-leitlinien.html"
            response = await self._get_with_retry(url)
            soup = self._parse_html(response.text)

            # Extract recent guidelines - this needs to be adjusted based on actual AWMF structure
            results = []
            guideline_elements = soup.select("div.recent-guideline")[:limit]

            for elem in guideline_elements:
                try:
                    title_elem = elem.select_one("h3 a")
                    if not title_elem:
                        continue

                    title = title_elem.text.strip()
                    url = title_elem["href"]
                    if not url.startswith("http"):
                        url = f"{self.base_url}{url}"

                    source_id = self._generate_document_id(url)

                    results.append(SearchResult(
                        title=title,
                        url=url,
                        source=self.source,
                        source_id=source_id,
                        raw_data={"html": str(elem)}
                    ))

                except Exception as e:
                    logger.error(f"Error parsing recent guideline: {str(e)}")
                    continue

            return results

        except Exception as e:
            logger.error(f"Error getting recent guidelines: {str(e)}")
            return []

# Note: The actual implementation would require analyzing the real AWMF website structure
# and adjusting the CSS selectors and parsing logic accordingly.
# This is a template that provides the structure and can be completed once the actual
# website structure is known.
