"""
DramaBox API Client
Client untuk berinteraksi dengan DramaBox API
"""

import aiohttp
import logging
from typing import Optional, List, Dict
from .models import Drama, Episode

logger = logging.getLogger(__name__)


class DramaBoxAPI:
    """Client untuk DramaBox API"""
    
    def __init__(self, base_url: str = "https://dramabox.sansekai.my.id/api"):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get atau create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _request(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Melakukan request ke API"""
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        try:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Error saat request ke {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def get_trending(self, limit: int = 10) -> list[Drama]:
        """Ambil daftar drama trending"""
        try:
            data = await self._request("/dramabox/trending")
            dramas = []
            
            # API returns list directly
            items = data[:limit] if isinstance(data, list) else []
            
            for item in items:
                drama = Drama(
                    book_id=str(item.get("bookId", "")),
                    title=item.get("bookName", "Unknown"),
                    cover_url=item.get("coverWap", ""),
                    description=item.get("introduction", ""),
                    episode_count=int(item.get("chapterCount", 0)),
                    category=None,  # Not in response
                    rating=None,  # Not in response
                    views=item.get("rankVo", {}).get("hotCode") if item.get("rankVo") else None,
                )
                dramas.append(drama)
            
            return dramas
        except Exception as e:
            logger.error(f"Error get_trending: {e}")
            return []
    
    async def get_latest(self, limit: int = 10) -> list[Drama]:
        """Ambil daftar drama terbaru"""
        try:
            data = await self._request("/dramabox/latest")
            dramas = []
            
            # API returns list directly
            items = data[:limit] if isinstance(data, list) else []
            
            for item in items:
                drama = Drama(
                    book_id=str(item.get("bookId", "")),
                    title=item.get("bookName", "Unknown"),
                    cover_url=item.get("coverWap", ""),
                    description=item.get("introduction", ""),
                    episode_count=int(item.get("chapterCount", 0)),
                    category=None,
                    rating=None,
                    views=item.get("rankVo", {}).get("hotCode") if item.get("rankVo") else None,
                )
                dramas.append(drama)
            
            return dramas
        except Exception as e:
            logger.error(f"Error get_latest: {e}")
            return []
    
    async def search(self, query: str, limit: int = 10) -> list[Drama]:
        """Cari drama berdasarkan query"""
        try:
            data = await self._request("/dramabox/search", params={"query": query})
            dramas = []
            
            # API returns list directly
            items = data[:limit] if isinstance(data, list) else []
            
            for item in items:
                drama = Drama(
                    book_id=str(item.get("bookId", "")),
                    title=item.get("bookName", "Unknown"),
                    cover_url=item.get("cover", ""),
                    description=item.get("introduction", ""),
                    episode_count=int(item.get("chapterCount", 0)),
                    category=None,
                    rating=None,
                    views=item.get("rankVo", {}).get("hotCode") if item.get("rankVo") else None,
                    tags=item.get("tagNames", []),
                    protagonist=item.get("protagonist", "")
                )
                dramas.append(drama)
            
            # Cache the search results for later use in get_drama_detail
            self.search_cache = dramas
            
            return dramas
        except Exception as e:
            logger.error(f"Error search: {e}")
            return []

    def _get_best_url(self, urls: List[Dict]) -> str:
        """Helper to get best URL from list"""
        if not urls:
            return ""
        # Sort by quality descending
        sorted_urls = sorted(urls, key=lambda x: x.get("quality", 0), reverse=True)
        return sorted_urls[0].get("url", "")

    async def get_all_episodes(self, book_id: str) -> list[Episode]:
        """Ambil semua episode dari drama (dengan link streaming)"""
        try:
            data = await self._request("/dramabox/allepisode", params={"bookId": book_id})
            episodes = []
            
            # API returns list directly
            items = data if isinstance(data, list) else []
            
            for idx, item in enumerate(items, 1):  # Episode number from index
                urls = []
                # Iterate through all CDNs
                if isinstance(item.get("cdnList"), list):
                    for cdn in item["cdnList"]:
                        if isinstance(cdn.get("videoPathList"), list):
                            for v in cdn["videoPathList"]:
                                # Include all qualities (1080p, 720p, 540p)
                                urls.append({
                                    "quality": v.get("quality", 0),
                                    "url": v.get("videoPath", "")
                                })

                video_url = self._get_best_url(urls)
                
                episode = Episode(
                    book_id=book_id,
                    episode_num=idx,  # Use enumerate index as episode number
                    title=item.get("chapterName", f"Episode {idx}"),
                    video_url=video_url,
                    duration=item.get("duration"),
                    thumbnail=item.get("chapterImg"),
                    urls=urls
                )
                episodes.append(episode)
            
            return episodes
        except Exception as e:
            logger.error(f"Error get_all_episodes: {e}")
            return []
    
    async def get_episode(self, book_id: str, episode_num: int) -> Optional[Episode]:
        """Ambil satu episode spesifik"""
        episodes = await self.get_all_episodes(book_id)
        for ep in episodes:
            if ep.episode_num == episode_num:
                return ep
        return None
    
    async def get_drama_detail(self, book_id: str) -> Optional[Drama]:
        """Get drama detail by book_id - search in trending/latest/search cache"""
        try:
            # Check search cache first
            if hasattr(self, 'search_cache'):
                for drama in self.search_cache:
                    if drama.book_id == book_id:
                        return drama
            
            # Try trending
            trending = await self.get_trending(limit=50)
            for drama in trending:
                if drama.book_id == book_id:
                    return drama
            
            # Try latest
            latest = await self.get_latest(limit=50)
            for drama in latest:
                if drama.book_id == book_id:
                    return drama
            
            # If not found, return basic info
            episodes = await self.get_all_episodes(book_id)
            if episodes:
                return Drama(
                    book_id=book_id,
                    title=episodes[0].title.replace("EP 1", "").strip() or f"Drama {book_id}",
                    cover_url="",
                    description="",
                    episode_count=len(episodes),
                    category=None,
                    rating=None,
                    views=None
                )
            
            return None
        except Exception as e:
            logger.error(f"Error get_drama_detail: {e}")
            return None
    
    async def close(self):
        """Tutup session"""
        if self.session and not self.session.closed:
            await self.session.close()
