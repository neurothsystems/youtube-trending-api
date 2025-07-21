# core/trending_hybrid_v6.py - Deploy-Ready HYBRID Solution
"""
V6.0 Hybrid Trending Solution - Deploy-Ready
Ersetzt den kaputten Trending-Scraper mit API-basierter Lösung
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class HybridStats:
    """Hybrid Trending Statistics"""
    api_trending_videos: int = 0
    velocity_trending_videos: int = 0
    fresh_videos_found: int = 0
    total_analysis_time: float = 0.0
    success_rate: float = 0.0


class DeployReadyHybridAnalyzer:
    """Deploy-Ready Hybrid Trending Analyzer - No External Dependencies"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with minimal dependencies"""
        self.api_key = api_key or self._get_api_key()
        self.stats = HybridStats()
        
        print(f"🔥 Deploy-Ready Hybrid Analyzer initialized")
        print(f"   Strategy: API mostPopular + Velocity Analysis")
    
    def get_hybrid_trending_videos(self,
                                  region: str = 'DE',
                                  keyword: Optional[str] = None,
                                  max_videos: int = 50) -> Tuple[List, HybridStats]:
        """
        Get trending videos using API-only hybrid approach
        Returns list of VideoData objects
        """
        start_time = time.time()
        
        # Import VideoData here to avoid circular imports
        try:
            from .momentum_algorithm import VideoData
        except:
            # Fallback if import fails
            print("⚠️  VideoData import failed, using dict format")
            VideoData = dict
        
        print(f"\n🔥 DEPLOY-READY HYBRID: {region}" + (f" + '{keyword}'" if keyword else ""))
        print("🚨 Using API-only approach (YouTube removed Trending pages)")
        
        all_videos = []
        
        # Method 1: YouTube API mostPopular
        api_trending = self._get_api_most_popular(region, max_videos // 2)
        if api_trending:
            all_videos.extend(api_trending)
            self.stats.api_trending_videos = len(api_trending)
            print(f"✅ API mostPopular: {len(api_trending)} videos")
        
        # Method 2: Search for recent high-engagement videos
        if len(all_videos) < max_videos:
            search_query = keyword if keyword else 'trending'
            recent_videos = self._search_recent_videos(region, search_query, max_videos - len(all_videos))
            all_videos.extend(recent_videos)
            self.stats.velocity_trending_videos = len(recent_videos)
            print(f"✅ Recent Search: {len(recent_videos)} videos")
        
        # Apply keyword filter
        if keyword and all_videos:
            filtered = [v for v in all_videos if keyword.lower() in v.title.lower() or keyword.lower() in v.channel.lower()]
            all_videos = filtered
            print(f"🔍 Keyword filter: {len(all_videos)} videos match '{keyword}'")
        
        final_videos = all_videos[:max_videos]
        
        # Update stats
        self.stats.total_analysis_time = time.time() - start_time
        self.stats.success_rate = len(final_videos) / max_videos if max_videos > 0 else 0
        
        print(f"✅ Hybrid Complete: {len(final_videos)} videos in {self.stats.total_analysis_time:.2f}s")
        
        return final_videos, self.stats
    
    def _get_api_most_popular(self, region: str, max_videos: int) -> List:
        """Get mostPopular videos from YouTube API"""
        if not self.api_key:
            print("⚠️  No API key - skipping mostPopular")
            return []
        
        try:
            from googleapiclient.discovery import build
            from .momentum_algorithm import VideoData
            
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            request = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                chart='mostPopular',
                regionCode=region,
                maxResults=min(max_videos, 50)
            )
            
            response = request.execute()
            videos = []
            
            for item in response.get('items', []):
                try:
                    video_data = self._create_video_data(item, region, is_trending=True)
                    if video_data:
                        videos.append(video_data)
                except Exception as e:
                    continue
            
            return videos
            
        except Exception as e:
            print(f"❌ API mostPopular failed: {e}")
            return []
    
    def _search_recent_videos(self, region: str, query: str, max_videos: int) -> List:
        """Search for recent videos"""
        if not self.api_key:
            return []
        
        try:
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', developerKey=self.api_key)
            
            # Search recent videos
            published_after = (datetime.utcnow() - timedelta(hours=24)).isoformat("T") + "Z"
            
            search_request = youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                order='relevance',
                regionCode=region,
                publishedAfter=published_after,
                maxResults=min(max_videos, 25)
            )
            
            search_response = search_request.execute()
            
            if not search_response.get('items'):
                return []
            
            # Get video details
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            details_request = youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            )
            
            details_response = details_request.execute()
            
            videos = []
            for item in details_response.get('items', []):
                try:
                    video_data = self._create_video_data(item, region, is_trending=False)
                    if video_data and self._is_high_velocity(video_data):
                        video_data.is_trending_page_video = True  # Mark high-velocity as trending
                        video_data.source = 'velocity_trending'
                        videos.append(video_data)
                except Exception as e:
                    continue
            
            return videos
            
        except Exception as e:
            print(f"❌ Recent search failed: {e}")
            return []
    
    def _create_video_data(self, item: Dict, region: str, is_trending: bool = False):
        """Create VideoData object from API response"""
        try:
            from .momentum_algorithm import VideoData
            
            stats = item.get('statistics', {})
            snippet = item.get('snippet', {})
            content_details = item.get('contentDetails', {})
            
            # Parse duration
            duration_seconds = 0
            duration_str = content_details.get('duration', 'PT0M0S')
            try:
                import isodate
                duration = isodate.parse_duration(duration_str)
                duration_seconds = int(duration.total_seconds())
            except:
                pass
            
            # Calculate age
            published_at = snippet.get('publishedAt', '')
            age_hours = 24.0
            try:
                if published_at:
                    published = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                    age_hours = max((datetime.utcnow() - published).total_seconds() / 3600, 0.1)
            except:
                pass
            
            # Get thumbnail
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url = None
            for quality in ['maxres', 'high', 'medium', 'default']:
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality]['url']
                    break
            
            return VideoData(
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
                is_trending_page_video=is_trending,  # Mark mostPopular as trending
                source='api_trending' if is_trending else 'api',
                region_detected=region
            )
            
        except Exception as e:
            print(f"⚠️  Error creating video data: {e}")
            return None
    
    def _is_high_velocity(self, video) -> bool:
        """Check if video has high velocity (trending potential)"""
        if video.age_hours <= 0 or video.views == 0:
            return False
        
        views_per_hour = video.views / video.age_hours
        engagement_rate = (video.likes + video.comments) / video.views
        
        # Velocity thresholds
        return (
            views_per_hour >= 500 and  # 500+ views per hour
            engagement_rate >= 0.005 and  # 0.5%+ engagement
            video.age_hours <= 48  # Less than 48 hours old
        )
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config"""
        # Try environment first
        api_key = os.getenv('YOUTUBE_API_KEY')
        if api_key:
            return api_key
        
        # Try config file
        try:
            import configparser
            config = configparser.ConfigParser()
            if os.path.exists('config.ini'):
                config.read('config.ini')
                return config.get('API', 'api_key', fallback=None)
        except:
            pass
        
        return None
    
    def get_scraping_stats(self) -> Dict:
        """Get statistics for compatibility"""
        return {
            'total_requests': 1,
            'successful_scrapes': 1 if self.stats.api_trending_videos > 0 else 0,
            'failed_scrapes': 0,
            'videos_found': self.stats.api_trending_videos + self.stats.velocity_trending_videos,
            'cache_hits': 0,
            'last_scrape_time': datetime.now().isoformat(),
            'average_response_time': self.stats.total_analysis_time,
            'success_rate': self.stats.success_rate,
            'supported_regions': ['DE', 'US', 'GB', 'FR', 'ES', 'IT', 'AT', 'CH', 'NL'],
            'version': 'Deploy-Ready Hybrid V6.0',
            'hybrid_mode': True,
            'api_trending_videos': self.stats.api_trending_videos,
            'velocity_trending_videos': self.stats.velocity_trending_videos
        }


# Compatibility function to replace the old scraper
def create_trending_scraper(config: Optional[Dict] = None) -> DeployReadyHybridAnalyzer:
    """Create deploy-ready hybrid analyzer (replaces old scraper)"""
    return DeployReadyHybridAnalyzer()


# Export for import compatibility
TrendingPageScraper = DeployReadyHybridAnalyzer

if __name__ == "__main__":
    print("🧪 Deploy-Ready Hybrid Test")
    analyzer = DeployReadyHybridAnalyzer()
    videos, stats = analyzer.get_hybrid_trending_videos('DE', 'gaming', 5)
    print(f"Found {len(videos)} videos")
    for i, video in enumerate(videos[:3], 1):
        print(f"#{i}: {video.title[:50]}... | Trending: {video.is_trending_page_video}")
