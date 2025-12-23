"""
DramaBox API Models
Data structures untuk Drama dan Episode
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass
class Drama:
    """Model untuk Drama dari DramaBox API"""
    book_id: str
    title: str
    cover_url: str
    description: str
    episode_count: int
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    rating: Optional[float] = None
    views: Optional[str] = None
    
    def __str__(self):
        return f"{self.title} ({self.episode_count} episode)"


@dataclass
class Episode:
    """Model untuk Episode dari DramaBox API"""
    book_id: str
    episode_num: int
    title: str
    video_url: str
    duration: Optional[int] = None
    thumbnail: Optional[str] = None
    urls: List[Dict] = field(default_factory=list)
    
    def __str__(self):
        return f"Episode {self.episode_num}: {self.title}"
