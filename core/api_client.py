# core/api_client.py - V6.0 YouTube API Client
"""
V6.0 YouTube API Client
Clean wrapper for YouTube Data API v3 with caching and error handling
"""

import os
import time
import isodate
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .momentum_algorithm import VideoData


@dataclass
class APIQuotaInfo:
    """API Quota tracking information"""
    daily_limit: int = 10000
    used_today: int = 0
    requests_made: int = 0
    last_reset: Optional[str] = None
    cost_per_search: int = 100
    cost_per_video_details: int = 1


@dataclass
class APIStats:
    """API Usage Statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    quota_used: int = 0
    cache_hits: int = 0
    average_response_time: float = 0.0
    last_request_time: Optional[str] = None


class YouTubeAPIClient:
    """V6.0 YouTube API Client with smart caching and quota management"""
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 use_cache: bool = True,
                 cache_ttl: int = 3600,
                 quota_limit: int = 10000):
        """
        Initialize YouTube API Client
        
        Args:
            api_key: YouTube Data API key (if None, tries to get from env)
            use_cache: Enable request caching
            cache_ttl: Cache time-to-live in seconds
            quota_limit: Daily quota limit
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.use_cache = use_cache
        self.cache_ttl = cache_ttl
        
        # Initialize YouTube client
        if not self.api_key:
            raise ValueError("YouTube API key required. Set YOUTUBE_API_KEY environment variable or pass api_key parameter.")
        
        try:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
            print("✅ YouTube API client initialized")
        except Exception as e:
            raise ValueError(f"Failed to initialize YouTube API client: {e}")
        
        # Cache and statistics
        self.cache = {} if use_cache else None
        self.cache_timestamps = {} if use_cache else None
        
        self.quota_info = APIQuotaInfo(daily_limit=quota_limit)
        self.stats = APIStats()
        
        print(f"🔧 V6.0 YouTube API Client ready")
        print(f"   Cache enabled: {use_cache}")
        print(f"   Cache TTL: {cache_ttl}s")
        print(f"   Daily quota limit: {quota_limit}")
    
    def search_videos(self,
                     query: str,
                     region_code: str = 'DE',
                     max_results: int = 50,
                     order: str = 'relevance',
                     published_after_hours: int = 48) -> List[VideoData]:
        """
        Search for videos using YouTube API
        
        Args:
            query: Search query
            region_code: Region code (DE, US, GB, etc.)
            max_results: Maximum number of results
            order: Sort order (relevance, date, viewCount, etc.)
            published_after_hours: Only videos published within X hours
            
        Returns:
            List of VideoData objects
        """
        start_time = time.time()
        
        # Check cache
        cache_key = f"search_{query}_{region_code}_{max_results}_{order}_{published_after_hours}"
        if self._check_cache(cache_key):
            self.stats.cache_hits += 1
            print(f"💾 Cache HIT for search: {query}")
            return self.cache[cache_key]
        
        # Check quota
        if not self._check_quota(self.quota_info.cost_per_search):
            print(f"⚠️  Quota limit reached, returning empty results")
            return []
        
        try:
            print(f"🔍 API Search: '{query}' in {region_code}")
            
            # Calculate published_after timestamp
            published_after = (datetime.utcnow() - timedelta(hours=published_after_hours)).isoformat("T") + "Z"
            
            # Perform search
            search_request = self.youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=min(max_results, 50),  # API limit
                order=order,
                regionCode=region_code.upper(),
                publishedAfter=published_after,
                videoEmbeddable='true',
                videoSyndicated='true'
            )
            
            search_response = search_request.execute()
            self._update_stats(True, time.time() - start_time, self.quota_info.cost_per_search)
            
            if not search_response.get('items'):
                print(f"📊 No videos found for query: {query}")
                return []
            
            # Get video IDs for detailed information
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get detailed video information
            detailed_videos = self.get_video_details(video_ids, region_code)
            
            # Cache results
            if self.cache is not None:
                self._cache_result(cache_key, detailed_videos)
            
            print(f"✅ Found {len(detailed_videos)} videos for '{query}'")
            return detailed_videos
            
        except HttpError as e:
            self._update_stats(False, time.time() - start_time, 0)
            print(f"❌ YouTube API error: {e}")
            return []
        except Exception as e:
            self._update_stats(False, time.time() - start_time, 0)
            print(f"❌ Search error: {e}")
            return []
    
    def get_video_details(self, video_ids: List[str], region_code: str = 'DE') -> List[VideoData]:
        """
        Get detailed information for list of video IDs
        
        Args:
            video_ids: List of YouTube video IDs
            region_code: Region code for context
            
        Returns:
            List of VideoData objects with complete information
        """
        if not video_ids:
            return []
        
        start_time = time.time()
        
        # Check cache for bulk request
        cache_key = f"details_{','.join(sorted(video_ids))}_{region_code}"
        if self._check_cache(cache_key):
            self.stats.cache_hits += 1
            print(f"💾 Cache HIT for video details: {len(video_ids)} videos")
            return self.cache[cache_key]
        
        # Check quota
        quota_cost = len(video_ids)  # 1 unit per video
        if not self._check_quota(quota_cost):
            print(f"⚠️  Quota limit reached for video details")
            return []
        
        try:
            print(f"📊 Getting details for {len(video_ids)} videos")
            
            # YouTube API allows max 50 IDs per request
            detailed_videos = []
            
            for i in range(0, len(video_ids), 50):
                batch_ids = video_ids[i:i+50]
                
                details_request = self.youtube.videos().list(
                    part='statistics,snippet,contentDetails,status',
                    id=','.join(batch_ids)
                )
                
                details_response = details_request.execute()
                batch_videos = self._process_video_details(details_response, region_code)
                detailed_videos.extend(batch_videos)
            
            self._update_stats(True, time.time() - start_time, quota_cost)
            
            # Cache results
            if self.cache is not None:
                self._cache_result(cache_key, detailed_videos)
            
            print(f"✅ Retrieved details for {len(detailed_videos)} videos")
            return detailed_videos
            
        except HttpError as e:
            self._update_stats(False, time.time() - start_time, 0)
            print(f"❌ Video details API error: {e}")
            return []
        except Exception as e:
            self._update_stats(False, time.time() - start_time, 0)
            print(f"❌ Video details error: {e}")
            return []
    
    def _process_video_details(self, response: Dict, region_code: str) -> List[VideoData]:
        """Process video details response into VideoData objects"""
        videos = []
        
        for item in response.get('items', []):
            try:
                stats = item.get('statistics', {})
                snippet = item.get('snippet', {})
                content_details = item.get('contentDetails', {})
                status = item.get('status', {})
                
                # Skip private or unavailable videos
                if not status.get('embeddable', True) or status.get('privacyStatus') != 'public':
                    continue
                
                # Parse duration
                duration_seconds = 0
                duration_str = content_details.get('duration', 'PT0M0S')
                try:
                    duration = isodate.parse_duration(duration_str)
                    duration_seconds = int(duration.total_seconds())
                except:
                    duration_seconds = 0
                
                # Calculate age in hours
                age_hours = 24.0  # Default
                published_at = snippet.get('publishedAt', '')
                try:
                    if published_at:
                        published = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                        age_hours = max((datetime.utcnow() - published).total_seconds() / 3600, 0.1)
                except:
                    age_hours = 24.0
                
                # Get thumbnail URL
                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = None
                for quality in ['maxres', 'high', 'medium', 'default']:
                    if quality in thumbnails:
                        thumbnail_url = thumbnails[quality]['url']
                        break
                
                # Create VideoData object
                video = VideoData(
                    video_id=item['id'],
                    title=snippet.get('title', 'Unknown Title'),
                    channel=snippet.get('channelTitle', 'Unknown Channel'),
                    views=int(stats.get('viewCount', 0)),
                    comments=int(stats.get('commentCount', 0)),
                    likes=int(stats.get('likeCount', 0)),
                    duration_seconds=duration_seconds,
                    age_hours=age_hours,
                    published_at=published_at,
                    thumbnail=thumbnail_url,
                    is_trending_page_video=False,  # API videos are not from trending pages
                    source='api',
                    region_detected=region_code
                )
                
                videos.append(video)
                
            except Exception as e:
                print(f"⚠️  Error processing video {item.get('id', 'unknown')}: {e}")
                continue
        
        return videos
    
    def get_trending_videos(self, region_code: str = 'DE', max_results: int = 50) -> List[VideoData]:
        """
        Get trending videos for region using YouTube API
        Note: This gets "popular" videos, not necessarily trending
        
        Args:
            region_code: Region code
            max_results: Maximum number of results
            
        Returns:
            List of VideoData objects
        """
        start_time = time.time()
        
        # Check cache
        cache_key = f"trending_{region_code}_{max_results}"
        if self._check_cache(cache_key):
            self.stats.cache_hits += 1
            print(f"💾 Cache HIT for trending: {region_code}")
            return self.cache[cache_key]
        
        # Check quota
        if not self._check_quota(self.quota_info.cost_per_search):
            return []
        
        try:
            print(f"📈 Getting trending videos for {region_code}")
            
            # Get popular videos (YouTube's "trending" equivalent)
            request = self.youtube.videos().list(
                part='statistics,snippet,contentDetails',
                chart='mostPopular',
                regionCode=region_code.upper(),
                maxResults=min(max_results, 50)
            )
            
            response = request.execute()
            trending_videos = self._process_video_details(response, region_code)
            
            # Mark as API trending videos (different from scraped trending)
            for video in trending_videos:
                video.source = 'api_trending'
            
            self._update_stats(True, time.time() - start_time, self.quota_info.cost_per_search)
            
            # Cache results
            if self.cache is not None:
                self._cache_result(cache_key, trending_videos)
            
            print(f"✅ Retrieved {len(trending_videos)} trending videos")
            return trending_videos
            
        except Exception as e:
            self._update_stats(False, time.time() - start_time, 0)
            print(f"❌ Trending videos error: {e}")
            return []
    
    def _check_cache(self, cache_key: str) -> bool:
        """Check if cache entry exists and is valid"""
        if not self.cache or cache_key not in self.cache:
            return False
        
        # Check expiration
        if cache_key in self.cache_timestamps:
            cache_time = self.cache_timestamps[cache_key]
            if time.time() - cache_time > self.cache_ttl:
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
                return False
        
        return True
    
    def _cache_result(self, cache_key: str, result: List[VideoData]):
        """Cache API result"""
        if self.cache is not None:
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = time.time()
    
    def _check_quota(self, cost: int) -> bool:
        """Check if quota allows for request"""
        # Reset quota if new day
        now = datetime.now()
        if self.quota_info.last_reset:
            last_reset = datetime.fromisoformat(self.quota_info.last_reset)
            if now.date() > last_reset.date():
                self.quota_info.used_today = 0
                self.quota_info.last_reset = now.isoformat()
        else:
            self.quota_info.last_reset = now.isoformat()
        
        # Check if request would exceed quota
        if self.quota_info.used_today + cost > self.quota_info.daily_limit:
            return False
        
        return True
    
    def _update_stats(self, success: bool, response_time: float, quota_cost: int):
        """Update API statistics"""
        self.stats.total_requests += 1
        
        if success:
            self.stats.successful_requests += 1
            self.quota_info.used_today += quota_cost
            self.stats.quota_used += quota_cost
        else:
            self.stats.failed_requests += 1
        
        # Update average response time
        total_time = self.stats.average_response_time * (self.stats.total_requests - 1) + response_time
        self.stats.average_response_time = total_time / self.stats.total_requests
        
        self.stats.last_request_time = datetime.now().isoformat()
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get comprehensive API statistics"""
        success_rate = 0.0
        if self.stats.total_requests > 0:
            success_rate = self.stats.successful_requests / self.stats.total_requests
        
        cache_hit_rate = 0.0
        total_requests_cache = self.stats.total_requests + self.stats.cache_hits
        if total_requests_cache > 0:
            cache_hit_rate = self.stats.cache_hits / total_requests_cache
        
        return {
            'api_statistics': {
                'total_requests': self.stats.total_requests,
                'successful_requests': self.stats.successful_requests,
                'failed_requests': self.stats.failed_requests,
                'success_rate': f"{success_rate:.1%}",
                'average_response_time': f"{self.stats.average_response_time:.2f}s",
                'last_request': self.stats.last_request_time
            },
            'quota_info': {
                'daily_limit': self.quota_info.daily_limit,
                'used_today': self.quota_info.used_today,
                'remaining_today': self.quota_info.daily_limit - self.quota_info.used_today,
                'usage_percentage': f"{(self.quota_info.used_today / self.quota_info.daily_limit * 100):.1f}%"
            },
            'cache_stats': {
                'enabled': self.use_cache,
                'cache_hits': self.stats.cache_hits,
                'cache_hit_rate': f"{cache_hit_rate:.1%}",
                'cache_ttl_seconds': self.cache_ttl,
                'cached_entries': len(self.cache) if self.cache else 0
            },
            'version': 'V6.0'
        }
    
    def clear_cache(self):
        """Clear API cache"""
        if self.cache:
            entries_cleared = len(self.cache)
            self.cache.clear()
            self.cache_timestamps.clear()
            print(f"🗑️  Cleared {entries_cleared} cache entries")
    
    def test_connection(self) -> bool:
        """Test YouTube API connection"""
        try:
            print("🧪 Testing YouTube API connection...")
            
            # Simple test request
            request = self.youtube.search().list(
                q='test',
                part='snippet',
                type='video',
                maxResults=1
            )
            
            response = request.execute()
            
            print("✅ YouTube API connection successful")
            return True
            
        except Exception as e:
            print(f"❌ YouTube API connection failed: {e}")
            return False


def create_api_client(api_key: Optional[str] = None, **kwargs) -> YouTubeAPIClient:
    """Factory function for YouTube API Client"""
    return YouTubeAPIClient(api_key=api_key, **kwargs)


# Test function
if __name__ == "__main__":
    print("🧪 V6.0 YouTube API Client Test")
    print("=" * 50)
    
    try:
        # Initialize client
        client = YouTubeAPIClient()
        
        # Test connection
        if client.test_connection():
            print("✅ API Client ready for testing")
            
            # Test search
            print(f"\n🔍 Testing search...")
            videos = client.search_videos('gaming', 'DE', max_results=5)
            print(f"Found {len(videos)} videos")
            
            for i, video in enumerate(videos[:3], 1):
                print(f"   #{i}: {video.title[:50]}... | {video.views:,} views | {video.age_hours:.1f}h old")
            
            # Test trending
            print(f"\n📈 Testing trending...")
            trending = client.get_trending_videos('DE', max_results=3)
            print(f"Found {len(trending)} trending videos")
            
            for i, video in enumerate(trending, 1):
                print(f"   #{i}: {video.title[:50]}... | {video.views:,} views")
            
            # Show statistics
            print(f"\n📊 API Statistics:")
            stats = client.get_api_stats()
            print(f"   Requests: {stats['api_statistics']['total_requests']}")
            print(f"   Success Rate: {stats['api_statistics']['success_rate']}")
            print(f"   Quota Used: {stats['quota_info']['used_today']}/{stats['quota_info']['daily_limit']}")
            print(f"   Cache Hit Rate: {stats['cache_stats']['cache_hit_rate']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("💡 Make sure YOUTUBE_API_KEY environment variable is set")
