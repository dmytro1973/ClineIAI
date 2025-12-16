import abc
import logging
from typing import Optional, Dict, Any, List, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
import httpx
import tenacity
from bs4 import BeautifulSoup
import asyncio
import hashlib

# Configure logging
logger = logging.getLogger(__name__)

class ScraperConfig(BaseModel):
    """Configuration for web scrapers"""
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit: Optional[int] = None
    concurrent_requests: int = 5
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1 hour in seconds

class SearchResult(BaseModel):
    """Standardized search result"""
    title: str
    url: str
    source: str
    source_id: str
    authors: Optional[List[str]] = None
    published_date: Optional[datetime] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None

class DocumentMetadata(BaseModel):
    """Document metadata"""
    title: str
    authors: Optional[List[str]] = None
    published_date: Optional[datetime] = None
    publisher: Optional[str] = None
    doi: Optional[str] = None
    pmc_id: Optional[str] = None
    pm_id: Optional[str] = None
    language: Optional[str] = None
    keywords: Optional[List[str]] = None
    abstract: Optional[str] = None

class BaseScraper(abc.ABC):
    """Abstract base class for web scrapers"""

    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        self.client = self._create_http_client()
        self.semaphore = asyncio.Semaphore(self.config.concurrent_requests)
        self.cache: Dict[str, Tuple[datetime, Any]] = {}

    def _create_http_client(self) -> httpx.AsyncClient:
        """Create HTTP client with configured settings"""
        headers = {
            "User-Agent": self.config.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
        }

        # Configure retry strategy
        retry_strategy = tenacity.Retrying(
            stop=tenacity.stop_after_attempt(self.config.max_retries),
            wait=tenacity.wait_exponential(
                multiplier=self.config.retry_delay,
                min=1,
                max=10
            ),
            retry=tenacity.retry_if_exception_type(
                httpx.RequestError
            ),
            reraise=True
        )

        return httpx.AsyncClient(
            headers=headers,
            timeout=self.config.timeout,
            follow_redirects=True,
            http2=True
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """Generate cache key for URL and parameters"""
        if params:
            # Sort parameters for consistent caching
            sorted_params = sorted(params.items())
            param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
            return f"{url}?{param_str}"
        return url

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached item is still valid"""
        if not self.config.cache_enabled:
            return False

        if cache_key not in self.cache:
            return False

        cached_at, _ = self.cache[cache_key]
        return (datetime.now() - cached_at).total_seconds() < self.config.cache_ttl

    def _add_to_cache(self, cache_key: str, data: Any):
        """Add data to cache"""
        if self.config.cache_enabled:
            self.cache[cache_key] = (datetime.now(), data)

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            _, data = self.cache[cache_key]
            return data
        return None

    async def _rate_limit(self):
        """Apply rate limiting if configured"""
        if self.config.rate_limit:
            await asyncio.sleep(60 / self.config.rate_limit)

    async def _get_with_retry(self, url: str, params: Optional[Dict] = None) -> httpx.Response:
        """Make HTTP GET request with retry logic"""
        cache_key = self._get_cache_key(url, params)

        # Check cache first
        cached_response = self._get_from_cache(cache_key)
        if cached_response is not None:
            logger.debug(f"Cache hit for {url}")
            return cached_response

        async with self.semaphore:
            try:
                # Apply rate limiting
                await self._rate_limit()

                logger.debug(f"Fetching {url}")
                response = await self.client.get(url, params=params)
                response.raise_for_status()

                # Cache the response
                self._add_to_cache(cache_key, response)
                return response

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for {url}: {str(e)}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error for {url}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {str(e)}")
                raise

    async def _post_with_retry(self, url: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> httpx.Response:
        """Make HTTP POST request with retry logic"""
        async with self.semaphore:
            try:
                # Apply rate limiting
                await self._rate_limit()

                logger.debug(f"POST to {url}")
                response = await self.client.post(url, data=data, json=json)
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code} for {url}: {str(e)}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error for {url}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error for {url}: {str(e)}")
                raise

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'lxml')

    def _generate_document_id(self, url: str, source_id: Optional[str] = None) -> str:
        """Generate unique document ID"""
        if source_id:
            return f"{self.source}:{source_id}"
        return f"{self.source}:{hashlib.sha256(url.encode()).hexdigest()}"

    @abc.abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[SearchResult]:
        """Search for documents"""
        pass

    @abc.abstractmethod
    async def get_document_details(self, source_id: str) -> DocumentMetadata:
        """Get detailed metadata for a document"""
        pass

    @abc.abstractmethod
    async def download_document(self, source_id: str, output_path: str) -> bool:
        """Download document to specified path"""
        pass

    @property
    @abc.abstractmethod
    def source(self) -> str:
        """Source identifier"""
        pass

    @property
    @abc.abstractmethod
    def source_name(self) -> str:
        """Human-readable source name"""
        pass

    @property
    @abc.abstractmethod
    def base_url(self) -> str:
        """Base URL for the source"""
        pass

    @property
    @abc.abstractmethod
    def requires_authentication(self) -> bool:
        """Whether this source requires authentication"""
        pass

class ScraperFactory:
    """Factory for creating scrapers"""

    @staticmethod
    def create_scraper(source: str, config: Optional[ScraperConfig] = None) -> 'BaseScraper':
        """Create scraper instance based on source"""
        from .awmf import AWMFScraper
        from .who import WHOScraper
        from .springer import SpringerScraper

        scrapers = {
            'awmf': AWMFScraper,
            'who': WHOScraper,
            'springer': SpringerScraper,
        }

        if source.lower() not in scrapers:
            raise ValueError(f"Unknown scraper source: {source}")

        return scrapers[source.lower()](config)
