# core/trending_scraper_fixed.py - V6.0 Trending Scraper mit Fixes
"""
V6.0 YouTube Trending Pages Scraper - Verbesserte Version
Behebt die Scraping-Probleme für echte Trending-Videos
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
import urllib.parse


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


class ImprovedTrendingPageScraper:
    """V6.0 YouTube Trending Pages Scraper - Fixed Version"""
    
    # Aktualisierte Trending URLs (2024)
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
    }
    
    # Verbesserte User Agents (2024)
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0'
    ]
    
    def __init__(self, 
                 request_timeout: int = 20,
                 max_retries: int = 3,
                 delay_between_requests: float = 2.0,
                 use_cache: bool = True,
                 cache_ttl: int = 300):
        """
        Initialize V6.0 Improved Trending Scraper
        """
        self.request_timeout = request_timeout
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        
        # Setup session with better headers
        self.session = requests.Session()
        self._update_headers()
        
        # Cache
        self.cache = {} if use_cache else None
        self.cache_timestamps = {} if use_cache else None
        
        # Statistics
        self.stats = ScrapingStats()
        
        print(f"🔥 V6.0 Improved Trending Scraper initialized")
        print(f"   Enhanced anti-detection measures")
        print(f"   Multiple fallback methods")
        print(f"   Supported regions: {', '.join(self.TRENDING_URLS.keys())}")
    
    def scrape_trending_videos(self, 
                              region: str = 'DE',
                              keyword: Optional[str] = None,
                              max_videos: int = 50) -> Tuple[List[VideoData], ScrapingStats]:
        """
        Scrape trending videos with improved detection
        """
        start_time = time.time()
        region = region.upper()
        
        print(f"\n🔥 V6.0 IMPROVED SCRAPER: {region}" + (f" + '{keyword}'" if keyword else ""))
        print("=" * 60)
        
        # Check cache first
        cache_key = f"{region}_{keyword}_{max_videos}"
        if self._check_cache(cache_key):
            cached_result = self.cache[cache_key]
            self.stats.cache_hits += 1
            print(f"💾 Cache HIT: {len(cached_result)} videos from cache")
            return cached_result, self.stats
        
        # Try multiple methods
        videos = []
        
        # Method 1: Direct trending page scraping
        print("🌐 Method 1: Direct trending page...")
        trending_videos = self._scrape_trending_page_improved(region, max_videos)
        if trending_videos:
            videos.extend(trending_videos)
            print(f"✅ Direct scraping: {len(trending_videos)} videos")
        else:
            print("❌ Direct scraping failed")
        
        # Method 2: Alternative trending URLs (if Method 1 fails)
        if len(videos) < max_videos // 2:
            print("🔄 Method 2: Alternative URLs...")
            alt_videos = self._try_alternative_urls(region, max_videos - len(videos))
            videos.extend(alt_videos)
            print(f"✅ Alternative URLs: {len(alt_videos)} additional videos")
        
        # Method 3: YouTube search for trending content (fallback)
        if len(videos) < 5:
            print("🔄 Method 3: Fallback search...")
            fallback_videos = self._fallback_trending_search(region, max_videos)
            videos.extend(fallback_videos)
            print(f"✅ Fallback search: {len(fallback_videos)} videos")
        
        # Apply keyword filter if specified
        if keyword and videos:
            filtered_videos = self._filter_by_keyword(videos, keyword)
            print(f"🔍 Keyword filter '{keyword}': {len(videos)} → {len(filtered_videos)} videos")
            videos = filtered_videos
        
        # Convert to VideoData objects
        video_data_list = []
        for video_info in videos[:max_videos]:
            video_data = self._convert_to_video_data(video_info, region)
            if video_data:
                video_data_list.append(video_data)
        
        # Update statistics
        self.stats.successful_scrapes += 1
        self.stats.videos_found = len(video_data_list)
        self.stats.last_scrape_time = datetime.now().isoformat()
        self.stats.average_response_time = time.time() - start_time
        
        # Cache results
        if self.cache is not None and video_data_list:
            self._cache_result(cache_key, video_data_list)
        
        print(f"✅ V6.0 Improved Scraping: {len(video_data_list)} trending videos")
        print(f"⏱️  Response time: {self.stats.average_response_time:.2f}s")
        print("=" * 60)
        
        return video_data_list, self.stats
    
    def _scrape_trending_page_improved(self, region: str, max_videos: int) -> List[Dict]:
        """Improved trending page scraping with better parsing"""
        url = self.TRENDING_URLS.get(region, self.TRENDING_URLS['DE'])
        
        for attempt in range(self.max_retries):
            try:
                # Rotate user agent and add delays
                self._update_headers()
                if attempt > 0:
                    delay = self.delay_between_requests * (attempt + 1) + random.uniform(1, 3)
                    print(f"⏳ Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                
                print(f"🌐 Fetching (attempt {attempt + 1}): {url}")
                response = self.session.get(url, timeout=self.request_timeout)
                response.raise_for_status()
                
                # Parse with improved methods
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Method A: Try new YouTube structure
                videos = self._extract_videos_new_structure(soup, max_videos)
                if videos:
                    print(f"✅ New structure parsing: {len(videos)} videos")
                    return videos
                
                # Method B: Try legacy structure
                videos = self._extract_videos_legacy_structure(soup, max_videos)
                if videos:
                    print(f"✅ Legacy structure parsing: {len(videos)} videos")
                    return videos
                
                # Method C: Try JSON extraction
                videos = self._extract_videos_from_json(response.text, max_videos)
                if videos:
                    print(f"✅ JSON extraction: {len(videos)} videos")
                    return videos
                
                print(f"⚠️  No videos found in attempt {attempt + 1}")
                
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed: {e}")
        
        return []
    
    def _extract_videos_new_structure(self, soup: BeautifulSoup, max_videos: int) -> List[Dict]:
        """Extract videos using 2024 YouTube structure"""
        videos = []
        seen_ids = set()
        
        # New YouTube selectors (2024)
        video_selectors = [
            'ytd-video-renderer',
            'ytd-rich-item-renderer',
            'ytd-grid-video-renderer',
            '[data-context-item-id]'
        ]
        
        for selector in video_selectors:
            video_elements = soup.select(selector)
            
            for element in video_elements:
                if len(videos) >= max_videos:
                    break
                
                # Extract video ID from various sources
                video_id = self._extract_video_id_from_element(element)
                if not video_id or video_id in seen_ids:
                    continue
                
                seen_ids.add(video_id)
                
                # Extract other information
                title = self._extract_title_from_element(element)
                channel = self._extract_channel_from_element(element)
                
                video_info = {
                    'video_id': video_id,
                    'title': title,
                    'channel': channel,
                    'url': f"https://youtube.com/watch?v={video_id}",
                    'source': 'trending_page_new',
                    'extraction_method': f'new_structure_{selector}'
                }
                
                videos.append(video_info)
            
            if len(videos) >= max_videos:
                break
        
        return videos
    
    def _extract_videos_legacy_structure(self, soup: BeautifulSoup, max_videos: int) -> List[Dict]:
        """Extract videos using legacy YouTube structure"""
        videos = []
        seen_ids = set()
        
        # Legacy selectors
        link_selectors = [
            'a[href*="/watch?v="]',
            'a[href*="youtube.com/watch"]',
            '[data-context-item-id] a',
        ]
        
        for selector in link_selectors:
            links = soup.select(selector)
            
            for link in links:
                if len(videos) >= max_videos:
                    break
                
                href = link.get('href', '')
                video_id = self._extract_video_id_from_url(href)
                
                if not video_id or video_id in seen_ids:
                    continue
                
                seen_ids.add(video_id)
                
                title = self._extract_title_from_link(link)
                channel = self._extract_channel_from_link(link)
                
                video_info = {
                    'video_id': video_id,
                    'title': title,
                    'channel': channel,
                    'url': f"https://youtube.com/watch?v={video_id}",
                    'source': 'trending_page_legacy',
                    'extraction_method': f'legacy_structure_{selector}'
                }
                
                videos.append(video_info)
            
            if len(videos) >= max_videos:
                break
        
        return videos
    
    def _extract_videos_from_json(self, html_content: str, max_videos: int) -> List[Dict]:
        """Extract videos from embedded JSON data"""
        videos = []
        seen_ids = set()
        
        # Look for JSON data in script tags
        json_patterns = [
            r'var ytInitialData = ({.*?});',
            r'window\["ytInitialData"\] = ({.*?});',
            r'"contents":.*?"videoRenderer":{(.*?)}',
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            
            for match in matches:
                try:
                    # Try to extract video IDs from JSON-like content
                    video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', match)
                    
                    for video_id in video_ids:
                        if len(videos) >= max_videos or video_id in seen_ids:
                            continue
                        
                        seen_ids.add(video_id)
                        
                        # Try to extract title and channel from nearby JSON
                        title_match = re.search(rf'"videoId":"{video_id}".*?"title".*?"text":"([^"]*)"', match)
                        title = title_match.group(1) if title_match else f"Video {video_id}"
                        
                        channel_match = re.search(rf'"videoId":"{video_id}".*?"channelName".*?"text":"([^"]*)"', match)
                        channel = channel_match.group(1) if channel_match else "Unknown Channel"
                        
                        video_info = {
                            'video_id': video_id,
                            'title': title,
                            'channel': channel,
                            'url': f"https://youtube.com/watch?v={video_id}",
                            'source': 'trending_page_json',
                            'extraction_method': 'json_extraction'
                        }
                        
                        videos.append(video_info)
                
                except Exception as e:
                    continue
        
        return videos
    
    def _try_alternative_urls(self, region: str, max_videos: int) -> List[Dict]:
        """Try alternative trending URLs"""
        alternative_urls = [
            f"https://www.youtube.com/feed/trending?gl={region}",
            f"https://m.youtube.com/feed/trending?gl={region}",
            f"https://www.youtube.com/trending?gl={region}",
        ]
        
        for url in alternative_urls:
            try:
                print(f"🔄 Trying alternative: {url}")
                response = self.session.get(url, timeout=self.request_timeout)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    videos = self._extract_videos_new_structure(soup, max_videos)
                    if videos:
                        return videos
            except Exception as e:
                continue
        
        return []
    
    def _fallback_trending_search(self, region: str, max_videos: int) -> List[Dict]:
        """Fallback: search for recent popular videos"""
        print("🔄 Using fallback: Recent popular videos...")
        
        # This would use YouTube search API if available
        # Or try to scrape search results for recent popular content
        # For now, return empty list
        return []
    
    def _extract_video_id_from_element(self, element) -> Optional[str]:
        """Extract video ID from various element types"""
        # Try data attributes
        video_id = element.get('data-context-item-id')
        if video_id:
            return video_id
        
        # Try href attributes in child links
        links = element.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            video_id = self._extract_video_id_from_url(href)
            if video_id:
                return video_id
        
        return None
    
    def _extract_video_id_from_url(self, url: str) -> Optional[str]:
        """Extract video ID from URL"""
        patterns = [
            r'[?&]v=([a-zA-Z0-9_-]{11})',
            r'/watch/([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'/embed/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_title_from_element(self, element) -> str:
        """Extract title from element"""
        title_selectors = [
            'h3 a',
            '[id*="video-title"]',
            '.video-title',
            'a[title]',
            'span[title]'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get('title') or title_elem.get_text(strip=True)
                if title and len(title) > 3:
                    return title
        
        return "Unknown Title"
    
    def _extract_channel_from_element(self, element) -> str:
        """Extract channel from element"""
        channel_selectors = [
            'a[href*="/channel/"]',
            'a[href*="/@"]',
            '.channel-name',
            '[class*="channel"]'
        ]
        
        for selector in channel_selectors:
            channel_elem = element.select_one(selector)
            if channel_elem:
                channel = channel_elem.get_text(strip=True)
                if channel and len(channel) > 2:
                    return channel
        
        return "Unknown Channel"
    
    def _extract_title_from_link(self, link) -> str:
        """Extract title from link element"""
        return link.get('title') or link.get_text(strip=True) or "Unknown Title"
    
    def _extract_channel_from_link(self, link) -> str:
        """Extract channel from link element context"""
        parent = link.parent
        if parent:
            channel_links = parent.find_all('a', href=True)
            for channel_link in channel_links:
                href = channel_link.get('href', '')
                if '/channel/' in href or '/@' in href:
                    return channel_link.get_text(strip=True) or "Unknown Channel"
        
        return "Unknown Channel"
    
    def _filter_by_keyword(self, videos: List[Dict], keyword: str) -> List[Dict]:
        """Filter videos by keyword"""
        keyword_lower = keyword.lower()
        filtered = []
        
        for video in videos:
            title_lower = video.get('title', '').lower()
            channel_lower = video.get('channel', '').lower()
            
            if (keyword_lower in title_lower or keyword_lower in channel_lower):
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
                comments=0,
                likes=0,
                duration_seconds=0,
                age_hours=1.0,  # Trending videos are assumed fresh
                published_at='',
                thumbnail=f"https://img.youtube.com/vi/{video_info['video_id']}/maxresdefault.jpg",
                is_trending_page_video=True,  # ✅ WICHTIG: This marks it as trending!
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
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def _check_cache(self, cache_key: str) -> bool:
        """Check cache validity"""
        if not self.cache or cache_key not in self.cache:
            return False
        
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
    
    def get_scraping_stats(self) -> Dict:
        """Get scraping statistics"""
        return {
            'total_requests': self.stats.total_requests,
            'successful_scrapes': self.stats.successful_scrapes,
            'failed_scrapes': self.stats.failed_scrapes,
            'videos_found': self.stats.videos_found,
            'cache_hits': self.stats.cache_hits,
            'last_scrape_time': self.stats.last_scrape_time,
            'average_response_time': self.stats.average_response_time,
            'success_rate': self.stats.successful_scrapes / max(self.stats.total_requests, 1),
            'supported_regions': list(self.TRENDING_URLS.keys()),
            'version': 'V6.0 Improved'
        }


# Factory function for improved scraper
def create_improved_trending_scraper(config: Optional[Dict] = None) -> ImprovedTrendingPageScraper:
    """Factory function for improved trending scraper"""
    if config:
        return ImprovedTrendingPageScraper(**config)
    else:
        return ImprovedTrendingPageScraper()


# Test the improved scraper
if __name__ == "__main__":
    print("🧪 V6.0 Improved Trending Scraper Test")
    print("=" * 50)
    
    scraper = ImprovedTrendingPageScraper()
    
    # Test different regions
    regions_to_test = ['DE', 'US']
    
    for region in regions_to_test:
        print(f"\n🌍 Testing region: {region}")
        videos, stats = scraper.scrape_trending_videos(region, max_videos=5)
        
        print(f"✅ Found {len(videos)} videos")
        for i, video in enumerate(videos[:3], 1):
            print(f"   #{i}: {video.title[:50]}... | {video.channel}")
            print(f"        Source: {video.source} | Trending: {video.is_trending_page_video}")
    
    # Show final stats
    final_stats = scraper.get_scraping_stats()
    print(f"\n📊 Final Statistics:")
    print(f"   Success Rate: {final_stats['success_rate']:.1%}")
    print(f"   Videos Found: {final_stats['videos_found']}")
    print(f"   Version: {final_stats['version']}")
