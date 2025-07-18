# core/trending_scraper.py - V6.0 YouTube Trending Pages Scraper
"""
V6.0 YouTube Trending Pages Scraper
Scrapt echte YouTube Trending-Seiten für präzise länderspezifische Trends
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from fake_useragent import UserAgent
from datetime import datetime
from .momentum_algorithm import VideoData


@dataclass
class ScrapingStats:
    """Scraping Statistics"""
    total_requests: int = 0
    successful_scrapes: int = 0
    failed_scrapes: int = 0
    videos_found: int = 0
    cache_hits: int = 0
    last_scrape_time: Optional[str] = None
    average_response_time: float = 0.0


class TrendingPageScraper:
    """V6.0 YouTube Trending Pages Scraper"""
    
    # Trending URLs für verschiedene Länder
    TRENDING_URLS = {
        'DE': 'https://www.youtube.com/feed/trending?gl=DE&hl=de',
        'US': 'https://www.youtube.com/feed/trending?gl=US&hl=en', 
        'GB': 'https://www.youtube.com/feed/trending?gl=GB&hl=en',
        'FR': 'https://www.youtube.com/feed/trending?gl=FR&hl=fr',
        'ES': 'https://www.youtube.com/feed/trending?gl=ES&hl=es',
        'IT': 'https://www.youtube.com/feed/trending?gl=IT&hl=it',
        'AT': 'https://www.youtube.com/feed/trending?gl=AT&hl=de',
        'CH': 'https://www.youtube.com/feed/trending?gl=CH&hl=de',
        'NL': 'https://www.youtube.com/feed/trending?gl=NL&hl=nl',
        'CA': 'https://www.youtube.com/feed/trending?gl=CA&hl=en',
        'AU': 'https://www.youtube.com/feed/trending?gl=AU&hl=en',
    }
    
    # User Agents Pool für bessere Success Rate
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
    ]
    
    def __init__(self, 
                 request_timeout: int = 15,
                 max_retries: int = 3,
                 delay_between_requests: float = 1.0,
                 use_cache: bool = True,
                 cache_ttl: int = 300):  # 5 minutes
        """
        Initialize V6.0 Trending Scraper
        
        Args:
            request_timeout: HTTP request timeout in seconds
            max_retries: Maximum retry attempts per request
            delay_between_requests: Delay between requests to be respectful
            use_cache: Enable caching of results
            cache_ttl: Cache time-to-live in seconds
        """
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        
        # Setup session with rotating user agents
        self.session = requests.Session()
        self._update_headers()
        
        # Simple in-memory cache
        self.cache = {} if use_cache else None
        self.cache_timestamps = {} if use_cache else None
        
        # Statistics tracking
        self.stats = ScrapingStats()
        
        print(f"🔥 V6.0 Trending Scraper initialized")
        print(f"   Supported regions: {', '.join(self.TRENDING_URLS.keys())}")
        print(f"   Cache enabled: {use_cache}")
        print(f"   Request timeout: {request_timeout}s")
    
    def scrape_trending_videos(self, 
                              region: str = 'DE',
                              keyword: Optional[str] = None,
                              max_videos: int = 50) -> Tuple[List[VideoData], ScrapingStats]:
        """
        Scrape trending videos for region with optional keyword filter
        
        Args:
            region: Target region code (DE, US, GB, etc.)
            keyword: Optional keyword to filter results
            max_videos: Maximum number of videos to return
            
        Returns:
            Tuple of (video_list, scraping_stats)
        """
        start_time = time.time()
        region = region.upper()
        
        print(f"\n🔥 V6.0 Trending Scraper: {region}" + (f" + '{keyword}'" if keyword else ""))
        print("=" * 60)
        
        # Check cache first
        cache_key = f"{region}_{keyword}_{max_videos}"
        if self._check_cache(cache_key):
            cached_result = self.cache[cache_key]
            self.stats.cache_hits += 1
            print(f"💾 Cache HIT: {len(cached_result)} videos from cache")
            return cached_result, self.stats
        
        try:
            # Scrape trending page
            raw_videos = self._fetch_trending_page(region, max_videos)
            
            if not raw_videos:
                raise Exception(f"No videos found for region {region}")
            
            # Apply keyword filter if specified
            if keyword:
                filtered_videos = self._filter_by_keyword(raw_videos, keyword)
                print(f"🔍 Keyword filter '{keyword}': {len(raw_videos)} → {len(filtered_videos)} videos")
                raw_videos = filtered_videos
            
            # Convert to VideoData objects
            video_data_list = []
            for video_info in raw_videos:
                video_data = self._convert_to_video_data(video_info, region)
                if video_data:
                    video_data_list.append(video_data)
            
            # Update statistics
            self.stats.successful_scrapes += 1
            self.stats.videos_found = len(video_data_list)
            self.stats.last_scrape_time = datetime.now().isoformat()
            self.stats.average_response_time = time.time() - start_time
            
            # Cache results
            if self.cache is not None:
                self._cache_result(cache_key, video_data_list)
            
            print(f"✅ V6.0 Scraping successful: {len(video_data_list)} trending videos")
            print(f"⏱️  Response time: {self.stats.average_response_time:.2f}s")
            print("=" * 60)
            
            return video_data_list, self.stats
            
        except Exception as e:
            self.stats.failed_scrapes += 1
            print(f"❌ V6.0 Scraping failed: {e}")
            print("=" * 60)
            return [], self.stats
    
    def _fetch_trending_page(self, region: str, max_videos: int) -> List[Dict]:
        """Fetch and parse trending page for region"""
        url = self.TRENDING_URLS.get(region, self.TRENDING_URLS['DE'])
        
        print(f"🌐 Fetching: {url}")
        self.stats.total_requests += 1
        
        for attempt in range(self.max_retries):
            try:
                # Rotate user agent for each attempt
                self._update_headers()
                
                # Add some jitter to avoid rate limiting
                if attempt > 0:
                    delay = self.delay_between_requests * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
                
                response = self.session.get(url, timeout=self.request_timeout)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                videos = self._extract_videos_from_html(soup, max_videos)
                
                print(f"📊 Extracted {len(videos)} videos from trending page")
                return videos
                
            except requests.exceptions.RequestException as e:
                print(f"⚠️  Attempt {attempt + 1}/{self.max_retries} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to fetch after {self.max_retries} attempts: {e}")
            
            except Exception as e:
                print(f"⚠️  Parsing error on attempt {attempt + 1}: {e}")
                if attempt == self.max_retries - 1:
                    raise Exception(f"Failed to parse page: {e}")
        
        return []
    
    def _extract_videos_from_html(self, soup: BeautifulSoup, max_videos: int) -> List[Dict]:
        """Extract video information from HTML soup"""
        videos = []
        seen_ids = set()
        
        # Method 1: Look for video links in various containers
        video_selectors = [
            'a[href*="/watch?v="]',
            'a[href*="youtube.com/watch"]',
            'ytd-video-renderer a[href*="/watch"]',
            'ytd-rich-item-renderer a[href*="/watch"]'
        ]
        
        for selector in video_selectors:
            video_links = soup.select(selector)
            
            for link in video_links:
                if len(videos) >= max_videos:
                    break
                    
                href = link.get('href', '')
                video_id = self._extract_video_id(href)
                
                if video_id and video_id not in seen_ids:
                    seen_ids.add(video_id)
                    
                    # Extract title
                    title = self._extract_title(link)
                    
                    # Extract channel (try to find nearby channel info)
                    channel = self._extract_channel(link)
                    
                    video_info = {
                        'video_id': video_id,
                        'title': title,
                        'channel': channel,
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'source': 'trending_page',
                        'extraction_method': selector
                    }
                    
                    videos.append(video_info)
            
            if len(videos) >= max_videos:
                break
        
        # Method 2: Try to extract from script tags (JSON data)
        if len(videos) < max_videos // 2:  # If we didn't get enough videos
            videos.extend(self._extract_from_scripts(soup, max_videos - len(videos), seen_ids))
        
        return videos[:max_videos]
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'[?&]v=([a-zA-Z0-9_-]{11})',
            r'/watch/([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_title(self, link_element) -> str:
        """Extract video title from link element"""
        # Try various attributes and methods
        title_sources = [
            link_element.get('title'),
            link_element.get('aria-label'),
            link_element.text.strip() if link_element.text else None
        ]
        
        # Look for title in child elements
        title_selectors = [
            'span[id*="video-title"]',
            'span.style-scope.ytd-video-renderer',
            'h3',
            'span'
        ]
        
        for selector in title_selectors:
            title_elem = link_element.select_one(selector)
            if title_elem and title_elem.text.strip():
                title_sources.append(title_elem.text.strip())
        
        # Return first non-empty title
        for title in title_sources:
            if title and len(title.strip()) > 0:
                return title.strip()
        
        return "Unknown Title"
    
    def _extract_channel(self, link_element) -> str:
        """Extract channel name from link element or nearby elements"""
        # Try to find channel info near the video link
        parent = link_element.parent
        if parent:
            # Look for channel links/info in parent containers
            channel_selectors = [
                'a[href*="/channel/"]',
                'a[href*="/@"]',
                'a[href*="/c/"]',
                'span.style-scope.ytd-channel-name'
            ]
            
            for selector in channel_selectors:
                channel_elem = parent.select_one(selector)
                if channel_elem and channel_elem.text.strip():
                    return channel_elem.text.strip()
        
        return "Unknown Channel"
    
    def _extract_from_scripts(self, soup: BeautifulSoup, needed_videos: int, seen_ids: set) -> List[Dict]:
        """Try to extract video data from script tags containing JSON"""
        videos = []
        
        script_tags = soup.find_all('script')
        
        for script in script_tags:
            if not script.string:
                continue
                
            try:
                # Look for patterns that might contain video data
                content = script.string
                
                # Look for video IDs in the script content
                video_id_matches = re.findall(r'"videoId":\s*"([a-zA-Z0-9_-]{11})"', content)
                
                for video_id in video_id_matches:
                    if len(videos) >= needed_videos:
                        break
                        
                    if video_id not in seen_ids:
                        seen_ids.add(video_id)
                        
                        # Try to extract title for this video ID
                        title_pattern = rf'"videoId":\s*"{video_id}".*?"title":\s*"([^"]*)"'
                        title_match = re.search(title_pattern, content)
                        title = title_match.group(1) if title_match else f"Video {video_id}"
                        
                        videos.append({
                            'video_id': video_id,
                            'title': title,
                            'channel': 'Unknown Channel',
                            'url': f"https://youtube.com/watch?v={video_id}",
                            'source': 'trending_page_script',
                            'extraction_method': 'script_parsing'
                        })
                
            except Exception as e:
                # Skip script tags that cause errors
                continue
        
        return videos
    
    def _filter_by_keyword(self, videos: List[Dict], keyword: str) -> List[Dict]:
        """Filter videos by keyword in title"""
        keyword_lower = keyword.lower()
        filtered = []
        
        for video in videos:
            title_lower = video.get('title', '').lower()
            channel_lower = video.get('channel', '').lower()
            
            if (keyword_lower in title_lower or 
                keyword_lower in channel_lower):
                video['keyword_match'] = True
                video['keyword_used'] = keyword
                filtered.append(video)
        
        return filtered
    
    def _convert_to_video_data(self, video_info: Dict, region: str) -> Optional[VideoData]:
        """Convert scraped video info to VideoData object"""
        try:
            return VideoData(
                video_id=video_info['video_id'],
                title=video_info['title'],
                channel=video_info['channel'],
                views=0,  # Will be filled by API enrichment
                comments=0,  # Will be filled by API enrichment
                likes=0,  # Will be filled by API enrichment
                duration_seconds=0,  # Will be filled by API enrichment
                age_hours=1.0,  # Trending videos are assumed to be fresh
                published_at='',  # Will be filled by API enrichment
                thumbnail=f"https://img.youtube.com/vi/{video_info['video_id']}/maxresdefault.jpg",
                is_trending_page_video=True,  # V6.0 marker
                source='trending_page',
                region_detected=region
            )
        except Exception as e:
            print(f"⚠️  Error converting video {video_info.get('video_id', 'unknown')}: {e}")
            return None
    
    def _update_headers(self):
        """Update session headers with random user agent"""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def _check_cache(self, cache_key: str) -> bool:
        """Check if cache entry exists and is still valid"""
        if not self.cache or cache_key not in self.cache:
            return False
        
        # Check if cache entry has expired
        if cache_key in self.cache_timestamps:
            cache_time = self.cache_timestamps[cache_key]
            if time.time() - cache_time > self.cache_ttl:
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
                return False
        
        return True
    
    def _cache_result(self, cache_key: str, result: List[VideoData]):
        """Cache scraping result"""
        if self.cache is not None:
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = time.time()
    
    def get_supported_regions(self) -> List[str]:
        """Get list of supported region codes"""
        return list(self.TRENDING_URLS.keys())
    
    def get_scraping_stats(self) -> Dict:
        """Get comprehensive scraping statistics"""
        stats_dict = {
            'total_requests': self.stats.total_requests,
            'successful_scrapes': self.stats.successful_scrapes,
            'failed_scrapes': self.stats.failed_scrapes,
            'videos_found': self.stats.videos_found,
            'cache_hits': self.stats.cache_hits,
            'last_scrape_time': self.stats.last_scrape_time,
            'average_response_time': self.stats.average_response_time,
            'success_rate': self.stats.successful_scrapes / max(self.stats.total_requests, 1),
            'cache_hit_rate': self.stats.cache_hits / max(self.stats.total_requests, 1),
            'supported_regions': self.get_supported_regions(),
            'cache_enabled': self.use_cache,
            'version': 'V6.0'
        }
        
        return stats_dict


def create_trending_scraper(config: Optional[Dict] = None) -> TrendingPageScraper:
    """Factory function for Trending Scraper"""
    if config:
        return TrendingPageScraper(**config)
    else:
        return TrendingPageScraper()


# Test Function
if __name__ == "__main__":
    # Test V6.0 Trending Scraper
    scraper = TrendingPageScraper()
    
    print("🧪 V6.0 Trending Scraper Test")
    print("=" * 50)
    
    # Test 1: Deutschland, alle Trending-Videos
    videos_de, stats_de = scraper.scrape_trending_videos('DE', max_videos=5)
    print(f"🇩🇪 Test 1 - DE Trending: {len(videos_de)} videos")
    for i, video in enumerate(videos_de[:3], 1):
        print(f"   #{i}: {video.title[:50]}... | {video.channel}")
    
    # Test 2: Deutschland, Gaming-Videos
    gaming_videos, gaming_stats = scraper.scrape_trending_videos('DE', 'gaming', max_videos=5)
    print(f"🎮 Test 2 - DE Gaming: {len(gaming_videos)} videos")
    for i, video in enumerate(gaming_videos[:3], 1):
        print(f"   #{i}: {video.title[:50]}... | {video.channel}")
    
    # Test 3: USA, alle Trending-Videos  
    videos_us, stats_us = scraper.scrape_trending_videos('US', max_videos=5)
    print(f"🇺🇸 Test 3 - US Trending: {len(videos_us)} videos")
    for i, video in enumerate(videos_us[:3], 1):
        print(f"   #{i}: {video.title[:50]}... | {video.channel}")
    
    # Statistics
    print(f"\n📊 Scraper Statistics:")
    final_stats = scraper.get_scraping_stats()
    print(f"   Success Rate: {final_stats['success_rate']:.1%}")
    print(f"   Cache Hit Rate: {final_stats['cache_hit_rate']:.1%}")
    print(f"   Average Response Time: {final_stats['average_response_time']:.2f}s")
    print(f"   Supported Regions: {len(final_stats['supported_regions'])}")
