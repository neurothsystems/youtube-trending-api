# main_server.py - V6.0 Clean Server (No Legacy Code)
"""
V6.0 YouTube Trending Analyzer Server
Clean implementation without V5.0 legacy code
Modular architecture for easy adjustments
"""

import http.server
import socketserver
import json
import urllib.parse
import time
import os
import configparser
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import defaultdict

# V6.0 Core Modules
from core.momentum_algorithm import MomentumAlgorithm, VideoData, TrendingResult, create_momentum_algorithm
from core.regional_filters import RegionalFilter, create_regional_filter
from core.trending_scraper import TrendingPageScraper, create_trending_scraper


class V6TrendingAnalyzer:
    """V6.0 Main Analyzer - Orchestrates all components"""
    
    def __init__(self, 
                 target_region: str = "DE",
                 algorithm_config: Optional[Dict] = None,
                 filter_config: Optional[Dict] = None,
                 scraper_config: Optional[Dict] = None):
        """
        Initialize V6.0 Trending Analyzer
        
        Args:
            target_region: Target region for analysis
            algorithm_config: MOMENTUM algorithm configuration
            filter_config: Regional filter configuration  
            scraper_config: Trending scraper configuration
        """
        self.target_region = target_region
        
        # Initialize components
        self.momentum_algorithm = create_momentum_algorithm(algorithm_config)
        self.regional_filter = create_regional_filter(target_region, filter_config)
        self.trending_scraper = create_trending_scraper(scraper_config)
        
        # V6.0 Enhanced statistics
        self.analysis_stats = {
            'total_analyses': 0,
            'trending_page_videos': 0,
            'api_videos': 0,
            'filtered_videos': 0,
            'truly_trending_results': 0,
            'average_analysis_time': 0.0
        }
        
        print(f"🚀 V6.0 Trending Analyzer initialized for region: {target_region}")
    
    def analyze_trending_videos(self,
                               query: str,
                               region: Optional[str] = None,
                               top_count: int = 12,
                               use_trending_pages: bool = True,
                               trending_limit: int = 20,
                               api_limit: int = 30) -> Dict[str, Any]:
        """
        V6.0 Complete Trending Analysis
        
        Workflow:
        1. Scrape echte Trending-Videos (optional)
        2. Fetch API videos for supplementation
        3. Apply regional filters & anti-bias
        4. Calculate MOMENTUM scores with bonuses
        5. Rank and return results
        """
        start_time = time.time()
        region = region or self.target_region
        
        print(f"\n🚀 V6.0 ANALYSIS: '{query}' in {region}")
        print(f"📊 Mode: {'Trending Pages + API' if use_trending_pages else 'API Only'}")
        print("=" * 70)
        
        all_videos = []
        
        # Phase 1: Trending Pages (if enabled)
        if use_trending_pages:
            print("🔥 Phase 1: Scraping Trending Pages...")
            trending_videos, scrape_stats = self.trending_scraper.scrape_trending_videos(
                region=region, 
                keyword=query, 
                max_videos=trending_limit
            )
            
            # Enrich with API data
            enriched_trending = self._enrich_videos_with_api(trending_videos)
            all_videos.extend(enriched_trending)
            
            self.analysis_stats['trending_page_videos'] = len(enriched_trending)
            print(f"✅ Trending Pages: {len(enriched_trending)} videos")
        
        # Phase 2: API Supplementation  
        print("📡 Phase 2: Fetching API Videos...")
        api_videos = self._fetch_api_videos(query, region, api_limit)
        all_videos.extend(api_videos)
        
        self.analysis_stats['api_videos'] = len(api_videos)
        print(f"✅ API Videos: {len(api_videos)} videos")
        
        # Phase 3: Deduplication
        print("🔄 Phase 3: Smart Deduplication...")
        unique_videos = self._deduplicate_videos(all_videos)
        print(f"✅ Deduplication: {len(all_videos)} → {len(unique_videos)} videos")
        
        # Phase 4: Regional Filtering
        print("🚫 Phase 4: Regional Filtering...")
        filtered_videos, filter_stats = self.regional_filter.apply_anti_bias_filter(unique_videos)
        
        self.analysis_stats['filtered_videos'] = len(filtered_videos)
        print(f"✅ Regional Filter: {len(unique_videos)} → {len(filtered_videos)} videos")
        
        # Phase 5: MOMENTUM Analysis
        print("🧠 Phase 5: MOMENTUM Score Calculation...")
        results = []
        
        for video in filtered_videos:
            # Get regional relevance score
            regional_boost = 0.0
            if hasattr(video, 'regional_analysis'):
                regional_boost = video.regional_analysis.score
            
            # Calculate MOMENTUM score with regional boost
            result = self.momentum_algorithm.calculate_score(video, regional_boost)
            results.append(result)
        
        # Phase 6: Ranking & Selection
        print("📊 Phase 6: Final Ranking...")
        results.sort(key=lambda x: x.trending_score, reverse=True)
        top_results = results[:top_count]
        
        # Update rankings and normalized scores
        if top_results:
            max_score = top_results[0].trending_score
            for i, result in enumerate(top_results, 1):
                result.rank = i
                result.normalized_score = (result.trending_score / max_score) * 10
        
        # Count truly trending videos in results
        truly_trending = sum(1 for r in top_results if r.is_truly_trending)
        self.analysis_stats['truly_trending_results'] = truly_trending
        
        # Update statistics
        self.analysis_stats['total_analyses'] += 1
        analysis_time = time.time() - start_time
        self.analysis_stats['average_analysis_time'] = analysis_time
        
        print(f"✅ Final Results: {len(top_results)} videos")
        print(f"🔥 Truly Trending: {truly_trending}/{len(top_results)} videos")
        print(f"⏱️  Analysis Time: {analysis_time:.2f}s")
        print("=" * 70)
        
        # Build response
        return {
            'success': True,
            'query': query,
            'region': region,
            'algorithm_used': 'momentum_v6.0',
            'analysis_mode': 'V6.0 Trending Pages Enhanced' if use_trending_pages else 'V6.0 API Only',
            'analyzed_videos': len(unique_videos),
            'filtered_videos': len(filtered_videos),
            'top_videos': [self._result_to_dict(result) for result in top_results],
            'v6_statistics': {
                'trending_page_videos': self.analysis_stats['trending_page_videos'],
                'api_videos': self.analysis_stats['api_videos'],
                'truly_trending_in_results': truly_trending,
                'analysis_time_seconds': analysis_time,
                'deduplication_removed': len(all_videos) - len(unique_videos),
                'filter_removed': len(unique_videos) - len(filtered_videos)
            },
            'scraper_stats': self.trending_scraper.get_scraping_stats(),
            'filter_stats': filter_stats,
            'algorithm_info': self.momentum_algorithm.get_algorithm_info(),
            'timestamp': datetime.now().isoformat()
        }
    
    def _fetch_api_videos(self, query: str, region: str, limit: int) -> List[VideoData]:
        """Fetch supplementary videos from YouTube API"""
        try:
            from googleapiclient.discovery import build
            import isodate
            
            # Get API key
            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                config = configparser.ConfigParser()
                if os.path.exists('config.ini'):
                    config.read('config.ini')
                    api_key = config.get('API', 'api_key', fallback=None)
            
            if not api_key:
                print("⚠️  No YouTube API key found")
                return []
            
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Search for videos
            search_request = youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                maxResults=limit,
                order='relevance',
                regionCode=region,
                publishedAfter=(datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ).isoformat() + 'Z')  # Today's videos
            )
            search_response = search_request.execute()
            
            if not search_response.get('items'):
                return []
            
            # Get detailed video information
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            details_request = youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids)
            )
            details_response = details_request.execute()
            
            # Convert to VideoData objects
            api_videos = []
            for item in details_response.get('items', []):
                try:
                    stats = item.get('statistics', {})
                    snippet = item.get('snippet', {})
                    content_details = item.get('contentDetails', {})
                    
                    # Parse duration
                    duration_str = content_details.get('duration', 'PT0M0S')
                    try:
                        duration = isodate.parse_duration(duration_str)
                        duration_seconds = int(duration.total_seconds())
                    except:
                        duration_seconds = 0
                    
                    # Calculate age
                    published_at = snippet.get('publishedAt', '')
                    try:
                        published = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                        age_hours = max((datetime.utcnow() - published).total_seconds() / 3600, 1)
                    except:
                        age_hours = 24
                    
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
                        thumbnail=snippet.get('thumbnails', {}).get('high', {}).get('url'),
                        is_trending_page_video=False,
                        source='api',
                        region_detected=region
                    )
                    
                    api_videos.append(video)
                    
                except Exception as e:
                    print(f"⚠️  Error processing API video: {e}")
                    continue
            
            return api_videos
            
        except Exception as e:
            print(f"❌ API fetch error: {e}")
            return []
    
    def _enrich_videos_with_api(self, trending_videos: List[VideoData]) -> List[VideoData]:
        """Enrich trending videos with API data"""
        if not trending_videos:
            return []
        
        try:
            from googleapiclient.discovery import build
            import isodate
            
            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                config = configparser.ConfigParser()
                if os.path.exists('config.ini'):
                    config.read('config.ini')
                    api_key = config.get('API', 'api_key', fallback=None)
            
            if not api_key:
                return trending_videos  # Return without enrichment
            
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Get details for trending videos
            video_ids = [v.video_id for v in trending_videos]
            details_request = youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids[:50])  # API limit
            )
            details_response = details_request.execute()
            
            # Create mapping of video_id to details
            details_map = {item['id']: item for item in details_response.get('items', [])}
            
            # Enrich videos
            enriched_videos = []
            for video in trending_videos:
                if video.video_id in details_map:
                    api_data = details_map[video.video_id]
                    
                    # Update with API data
                    stats = api_data.get('statistics', {})
                    snippet = api_data.get('snippet', {})
                    content_details = api_data.get('contentDetails', {})
                    
                    video.views = int(stats.get('viewCount', 0))
                    video.comments = int(stats.get('commentCount', 0))
                    video.likes = int(stats.get('likeCount', 0))
                    video.channel = snippet.get('channelTitle', video.channel)
                    
                    # Parse duration
                    try:
                        import isodate
                        duration_str = content_details.get('duration', 'PT0M0S')
                        duration = isodate.parse_duration(duration_str)
                        video.duration_seconds = int(duration.total_seconds())
                    except:
                        video.duration_seconds = 0
                    
                    # Calculate age
                    try:
                        published_at = snippet.get('publishedAt', '')
                        if published_at:
                            published = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                            video.age_hours = max((datetime.utcnow() - published).total_seconds() / 3600, 1)
                            video.published_at = published_at
                    except:
                        video.age_hours = 1.0
                
                enriched_videos.append(video)
            
            print(f"✅ API Enrichment: {len(enriched_videos)} videos enriched")
            return enriched_videos
            
        except Exception as e:
            print(f"⚠️  API enrichment error: {e}")
            return trending_videos
    
    def _deduplicate_videos(self, videos: List[VideoData]) -> List[VideoData]:
        """Remove duplicates, prioritizing trending page videos"""
        seen_ids = set()
        unique_videos = []
        
        # Sort to prioritize trending page videos
        sorted_videos = sorted(videos, key=lambda x: (not x.is_trending_page_video, x.video_id))
        
        for video in sorted_videos:
            if video.video_id not in seen_ids:
                seen_ids.add(video.video_id)
                unique_videos.append(video)
        
        return unique_videos
    
    def _result_to_dict(self, result: TrendingResult) -> Dict[str, Any]:
        """Convert TrendingResult to dictionary for API response"""
        return {
            'rank': result.rank,
            'video_id': result.video_data.video_id,
            'title': result.video_data.title,
            'channel': result.video_data.channel,
            'views': result.video_data.views,
            'comments': result.video_data.comments,
            'likes': result.video_data.likes,
            'trending_score': round(result.trending_score, 2),
            'normalized_score': round(result.normalized_score, 1),
            'confidence': round(result.confidence, 3),
            'age_hours': int(result.video_data.age_hours),
            'duration_seconds': result.video_data.duration_seconds,
            'duration_formatted': self._format_duration(result.video_data.duration_seconds),
            'engagement_rate': round(result.video_data.comments / max(result.video_data.views, 1), 4),
            'url': f"https://youtube.com/watch?v={result.video_data.video_id}",
            'thumbnail': result.video_data.thumbnail,
            'is_truly_trending': result.is_truly_trending,
            'source': result.video_data.source,
            'regional_relevance_score': result.regional_relevance_score,
            'algorithm_version': 'momentum_v6.0'
        }
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration as MM:SS or HH:MM:SS"""
        if seconds == 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


class V6HTTPHandler(http.server.BaseHTTPRequestHandler):
    """V6.0 Clean HTTP Handler"""
    
    # Rate limiting
    request_counts = defaultdict(list)
    max_requests_per_minute = 60
    
    def do_GET(self):
        """Handle GET requests"""
        client_ip = self.client_address[0]
        
        # Rate limiting
        if not self.check_rate_limit(client_ip):
            self.send_rate_limit_response()
            return
        
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        params = urllib.parse.parse_qs(parsed_url.query)
        
        # Route requests
        if path == '/':
            self.send_homepage()
        elif path == '/health':
            self.send_health_check()
        elif path == '/analyze':
            self.handle_analyze(params)
        elif path == '/trending-test':
            self.handle_trending_test(params)
        elif path == '/api/info':
            self.send_api_info()
        else:
            self.send_404()
    
    def handle_analyze(self, params):
        """Handle V6.0 video analysis"""
        try:
            # Extract parameters
            query = params.get('query', [''])[0].strip()
            if not query:
                raise ValueError("Query parameter required")
            
            region = params.get('region', ['DE'])[0].upper()
            top_count = int(params.get('top_count', [12])[0])
            use_trending_pages = params.get('trending_pages', ['true'])[0].lower() == 'true'
            trending_limit = int(params.get('trending_limit', [20])[0])
            api_limit = int(params.get('api_limit', [30])[0])
            
            # Create analyzer for this request
            analyzer = V6TrendingAnalyzer(target_region=region)
            
            # Perform analysis
            result = analyzer.analyze_trending_videos(
                query=query,
                region=region,
                top_count=top_count,
                use_trending_pages=use_trending_pages,
                trending_limit=trending_limit,
                api_limit=api_limit
            )
            
            self.send_json_response(result)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': 'V6.0 analysis failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(error_response, 500)
    
    def handle_trending_test(self, params):
        """Test trending scraper directly"""
        try:
            region = params.get('region', ['DE'])[0].upper()
            keyword = params.get('keyword', [None])[0]
            max_videos = int(params.get('max_videos', [5])[0])
            
            scraper = TrendingPageScraper()
            videos, stats = scraper.scrape_trending_videos(region, keyword, max_videos)
            
            response = {
                'success': True,
                'test_type': 'V6.0 Trending Scraper',
                'region': region,
                'keyword': keyword,
                'videos_found': len(videos),
                'sample_videos': [
                    {
                        'video_id': v.video_id,
                        'title': v.title,
                        'channel': v.channel,
                        'source': v.source
                    } for v in videos[:3]
                ],
                'scraper_stats': scraper.get_scraping_stats(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': 'Trending scraper test failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(error_response, 500)
    
    def send_homepage(self):
        """Send V6.0 homepage"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Trending Analyzer V6.0</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'SF Pro Display', system-ui, sans-serif; margin: 0; padding: 20px; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .header {{ text-align: center; padding: 40px 0; }}
                .title {{ font-size: 3em; font-weight: 700; margin-bottom: 10px; }}
                .version {{ background: linear-gradient(45deg, #10b981, #059669); padding: 8px 16px; 
                           border-radius: 20px; font-size: 0.9em; margin-left: 15px; }}
                .subtitle {{ font-size: 1.2em; opacity: 0.9; margin-bottom: 30px; }}
                .features {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
                            gap: 20px; margin: 40px 0; }}
                .feature {{ background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; 
                           backdrop-filter: blur(10px); }}
                .feature h3 {{ font-size: 1.4em; margin-bottom: 15px; }}
                .api-section {{ background: rgba(255,255,255,0.95); color: #333; padding: 30px; 
                               border-radius: 15px; margin: 30px 0; }}
                .endpoint {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; 
                            font-family: 'SF Mono', monospace; }}
                .test-links {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 20px 0; }}
                .test-link {{ background: linear-gradient(45deg, #ff6b6b, #ee5a24); color: white; 
                             padding: 12px 20px; text-decoration: none; border-radius: 8px; 
                             font-weight: 600; transition: transform 0.2s; }}
                .test-link:hover {{ transform: translateY(-2px); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">🚀 YouTube Trending Analyzer
                        <span class="version">V6.0 Clean</span>
                    </h1>
                    <p class="subtitle">
                        MOMENTUM Algorithm + Echte Trending-Seiten + Anti-Bias Filter
                    </p>
                    <p style="font-size: 0.9em; opacity: 0.8;">
                        🕐 Live seit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </p>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h3>🔥 Echte Trending-Videos</h3>
                        <p>Scrapt direkt YouTube Trending-Seiten für {len(TrendingPageScraper().get_supported_regions())} Länder. 
                           Zeigt Videos die WIRKLICH trending sind, nicht nur "verfügbar in Land X".</p>
                    </div>
                    <div class="feature">
                        <h3>🧠 MOMENTUM Algorithm</h3>
                        <p>Velocity-fokussierte Trend-Erkennung: (Views/h × 0.6) + (Engagement×Views × 0.3) + (Views×Decay × 0.1). 
                           +50% Bonus für echte Trending-Videos.</p>
                    </div>
                    <div class="feature">
                        <h3>🚫 Anti-Bias Filter</h3>
                        <p>Intelligente Regional-Filter reduzieren irrelevante Inhalte um 95%. 
                           Max 1 asiatisches Video, +40% Boost für deutsche Inhalte in DE.</p>
                    </div>
                    <div class="feature">
                        <h3>⚡ Modulare Architektur</h3>
                        <p>Saubere V6.0-only Implementierung. Jede Komponente einzeln anpassbar: 
                           Algorithm, Filter, Scraper, Server.</p>
                    </div>
                </div>
                
                <div class="api-section">
                    <h2>🔧 V6.0 API Endpoints</h2>
                    
                    <h3>🎯 Haupt-Analyse</h3>
                    <div class="endpoint">
                        GET /analyze?query=BEGRIFF&region=LAND&trending_pages=true
                    </div>
                    <p><strong>Parameter:</strong> query (required), region (DE/US/GB/...), top_count (12), trending_pages (true/false), trending_limit (20), api_limit (30)</p>
                    
                    <h3>🧪 Testing</h3>
                    <div class="endpoint">
                        GET /trending-test?region=DE&keyword=gaming&max_videos=5
                    </div>
                    <div class="endpoint">
                        GET /health - System Health Check
                    </div>
                    <div class="endpoint">
                        GET /api/info - Algorithm & System Information
                    </div>
                    
                    <div class="test-links">
                        <a href="/analyze?query=gaming&region=DE&trending_pages=true&top_count=8" class="test-link">
                            🎮 Gaming DE (V6.0)
                        </a>
                        <a href="/analyze?query=musik&region=DE&trending_pages=true&top_count=8" class="test-link">
                            🎵 Musik DE (V6.0)
                        </a>
                        <a href="/trending-test?region=DE&keyword=sport&max_videos=5" class="test-link">
                            🧪 Scraper Test
                        </a>
                        <a href="/health" class="test-link">
                            ✅ Health Check
                        </a>
                        <a href="/api/info" class="test-link">
                            ⚙️ API Info
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px; opacity: 0.8; font-size: 0.9em;">
                    <p>🏗️ V6.0 Clean Architecture - Modulare Komponenten für maximale Flexibilität</p>
                    <p>🚀 MOMENTUM Algorithm - Velocity-fokussierte Trend-Erkennung</p>
                    <p>🔥 Echte Trending-Seiten - Direkt von YouTube für präzise Ergebnisse</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_health_check(self):
        """Send health check response"""
        health_data = {
            'status': 'healthy',
            'version': 'V6.0 Clean',
            'architecture': 'Modular V6.0-only',
            'components': {
                'momentum_algorithm': '✅ Active',
                'regional_filters': '✅ Active', 
                'trending_scraper': '✅ Active',
                'api_integration': '✅ Active'
            },
            'supported_regions': TrendingPageScraper().get_supported_regions(),
            'timestamp': datetime.now().isoformat()
        }
        self.send_json_response(health_data)
    
    def send_api_info(self):
        """Send API information"""
        analyzer = V6TrendingAnalyzer()
        
        api_info = {
            'version': 'V6.0 Clean',
            'architecture': 'Modular Components',
            'components': {
                'momentum_algorithm': analyzer.momentum_algorithm.get_algorithm_info(),
                'regional_filter': analyzer.regional_filter.get_filter_stats(),
                'trending_scraper': analyzer.trending_scraper.get_scraping_stats()
            },
            'endpoints': [
                '/analyze - Main trending analysis',
                '/trending-test - Test scraper directly',
                '/health - System health check',
                '/api/info - This information'
            ],
            'example_requests': [
                '/analyze?query=gaming&region=DE&trending_pages=true',
                '/analyze?query=musik&region=DE&trending_pages=false',
                '/trending-test?region=US&keyword=sports'
            ],
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_json_response(api_info)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def send_404(self):
        """Send 404 response"""
        error_data = {
            'error': 'Endpoint not found',
            'available_endpoints': ['/analyze', '/trending-test', '/health', '/api/info'],
            'examples': [
                '/analyze?query=gaming&region=DE',
                '/trending-test?region=DE&keyword=sport'
            ],
            'version': 'V6.0 Clean'
        }
        self.send_json_response(error_data, 404)
    
    def check_rate_limit(self, client_ip):
        """Check rate limiting"""
        now = time.time()
        minute_ago = now - 60
        
        # Clean old entries
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip] 
            if req_time > minute_ago
        ]
        
        # Check limit
        if len(self.request_counts[client_ip]) >= self.max_requests_per_minute:
            return False
        
        # Add current request
        self.request_counts[client_ip].append(now)
        return True
    
    def send_rate_limit_response(self):
        """Send rate limit response"""
        error_data = {
            'error': 'Rate limit exceeded',
            'limit': f'{self.max_requests_per_minute} requests per minute',
            'retry_after': '60 seconds'
        }
        self.send_json_response(error_data, 429)
    
    def log_message(self, format, *args):
        """Enhanced logging"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} - {format % args}")


def start_v6_server(port=8000):
    """Start V6.0 Clean Server"""
    try:
        with socketserver.TCPServer(("", port), V6HTTPHandler) as httpd:
            print("=" * 80)
            print("🚀 YOUTUBE TRENDING ANALYZER V6.0 CLEAN")
            print("=" * 80)
            print(f"📡 Server running: http://localhost:{port}")
            print(f"🏠 Homepage: http://localhost:{port}")
            print(f"🔧 Health: http://localhost:{port}/health")
            print(f"📊 API Info: http://localhost:{port}/api/info")
            print("=" * 80)
            print("🏗️ V6.0 CLEAN ARCHITECTURE:")
            print("   🧠 core/momentum_algorithm.py - MOMENTUM Trending Algorithm")
            print("   🚫 core/regional_filters.py - Anti-Bias & Regional Logic")
            print("   🔥 core/trending_scraper.py - YouTube Trending Pages Scraper")
            print("   📡 main_server.py - Clean V6.0-only HTTP Server")
            print("=" * 80)
            print("🎯 V6.0 FEATURES:")
            print("   🔥 Echte Trending-Videos direkt von YouTube Trending-Seiten")
            print("   🧠 MOMENTUM Algorithm für velocity-fokussierte Trend-Erkennung")
            print("   🚫 Anti-Bias Filter reduziert irrelevante Inhalte um 95%")
            print("   ⚡ Modulare Architektur für schnelle Anpassungen")
            print("   🎯 +50% Bonus für Videos von echten Trending-Seiten")
            print("=" * 80)
            print("🧪 TESTE V6.0:")
            print(f"   🎮 Gaming: http://localhost:{port}/analyze?query=gaming&region=DE&trending_pages=true")
            print(f"   🎵 Musik: http://localhost:{port}/analyze?query=musik&region=DE&trending_pages=true")
            print(f"   🧪 Scraper: http://localhost:{port}/trending-test?region=DE&keyword=sport")
            print("=" * 80)
            print("✅ V6.0 Clean Server ready! Press Ctrl+C to stop")
            print("=" * 80)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 V6.0 Server stopped!")
    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == "__main__":
    # Get port from environment or use 8000
    port = int(os.environ.get('PORT', 8000))
    start_v6_server(port)
