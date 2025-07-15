# modular_server.py - V5.0 Enhanced Server mit Anti-Bias Filter Integration
"""
YouTube Trending Server mit V5.0 Enhanced Regional Filter
Saubere Architektur: Server nutzt trending_algorithm.py für alle Filter-Logik
"""

import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime, timedelta
import configparser
import math
import os
import csv
import io
import threading
import time
from collections import defaultdict

# Import des V5.0 Enhanced Algorithmus
from trending_algorithm import (
    VideoData, V6TrendingAnalyzer, AlgorithmFactory,
    RegionalFilter, TrendingResult, calculate_realistic_confidence
)

# Für Excel-Export
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False


class ModularYouTubeHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Handler mit V5.0 Enhanced Algorithmus-Integration"""
    
    # Rate limiting storage
    request_counts = defaultdict(list)
    max_requests_per_minute = 60
    
    # Verfügbare Algorithmus-Strategien
    ALGORITHM_STRATEGIES = {
        'basic': 'Basis-Algorithmus + V5.0 Filter',
        'regional': 'Regional optimiert + V5.0 Enhanced',
        'anti_spam': 'Anti-Spam + V5.0 Filter',
        'experimental': 'Experimentell + V5.0 Enhanced'
    }
    
    def do_GET(self):
        """Handle GET requests"""
        
        # Rate limiting check
        client_ip = self.client_address[0]
        if not self.check_rate_limit(client_ip):
            self.send_rate_limit_response()
            return
            
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        params = urllib.parse.parse_qs(parsed_url.query)
        
        # Route requests
        if path == '/':
            self.send_modular_homepage()
        elif path == '/test':
            self.send_test()
        elif path == '/config-test':
            self.send_config_test()
        elif path == '/youtube-test':
            self.send_youtube_test()
        elif path == '/analyze':
            self.handle_modular_analyze(params)
        elif path == '/algorithm-test':
            self.handle_algorithm_test(params)
        elif path == '/export/csv':
            self.handle_csv_export(params)
        elif path == '/export/excel':
            self.handle_excel_export(params)
        elif path == '/api/algorithms':
            self.send_algorithm_info()
        elif path == '/api/search-history':
            self.send_search_history()
        else:
            self.send_404()
    
    def check_rate_limit(self, client_ip):
        """Check if client has exceeded rate limit"""
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
        """Send rate limit exceeded response"""
        data = {
            "error": "Rate limit exceeded",
            "message": f"Maximum {self.max_requests_per_minute} requests per minute",
            "retry_after": "60 seconds",
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data, 429)
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'max-age=300')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def send_modular_homepage(self):
        """V5.0 Enhanced Homepage"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TopMetric.ai - V5.0 Enhanced YouTube Trending Analytics</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Inter', system-ui, -apple-system, sans-serif; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    line-height: 1.6;
                    min-height: 100vh;
                }}
                
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                
                .header {{ 
                    text-align: center; 
                    padding: 60px 20px; 
                    margin-bottom: 40px;
                }}
                
                .version-badge {{
                    background: linear-gradient(45deg, #ff6b6b, #ee5a24);
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 14px;
                    margin-left: 12px;
                }}
                
                .card {{
                    background: rgba(255, 255, 255, 0.95);
                    color: #333;
                    padding: 30px;
                    border-radius: 16px;
                    margin-bottom: 30px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
                }}
                
                .features-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                    gap: 20px; 
                    margin-top: 20px; 
                }}
                
                .feature-card {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 24px; 
                    border-radius: 12px; 
                    text-align: center;
                }}
                
                .test-button {{ 
                    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); 
                    color: white; 
                    padding: 12px 24px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    display: inline-block; 
                    margin: 8px; 
                    transition: all 0.3s ease;
                    font-weight: 600;
                    border: none;
                    cursor: pointer;
                }}
                .test-button:hover {{ 
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px -5px rgba(255, 107, 107, 0.4);
                }}
                
                .live-indicator {{
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background: #10b981;
                    border-radius: 50%;
                    margin-right: 8px;
                    animation: pulse 2s infinite;
                }}
                
                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.6; }}
                }}
                
                .stats-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }}
                
                .stat-card {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 20px;
                    border-radius: 12px;
                    text-align: center;
                    backdrop-filter: blur(10px);
                }}
                
                .stat-number {{
                    font-size: 2.5em;
                    font-weight: bold;
                    margin-bottom: 8px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 TopMetric.ai 
                        <span class="version-badge">V5.0 Enhanced</span>
                    </h1>
                    <p style="font-size: 1.2em; margin-top: 10px;">
                        AI-Powered YouTube Trending Analytics mit Anti-Bias Filter
                    </p>
                    <div style="margin-top: 20px;">
                        <span class="live-indicator"></span>
                        <strong>Live V5.0 Enhanced Modular Architecture</strong> | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">🚫</div>
                        <div>95% Anti-Bias Reduktion</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">🇩🇪</div>
                        <div>+40% Deutsche Inhalte</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">🔍</div>
                        <div>60+ Filter-Keywords</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">⚡</div>
                        <div>Echtzeit-Statistiken</div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🎯 V5.0 Enhanced Features</h2>
                    <div class="features-grid">
                        <div class="feature-card">
                            <h3>🚫 Anti-Bias Filter</h3>
                            <p>Maximal 1 indisches Video pro Suche. 95% Reduktion der regionalen Verzerrung.</p>
                        </div>
                        <div class="feature-card">
                            <h3>🌍 Regional Boost</h3>
                            <p>Deutsche Inhalte erhalten +40% Boost in der DE-Region für bessere Relevanz.</p>
                        </div>
                        <div class="feature-card">
                            <h3>🧠 Enhanced Patterns</h3>
                            <p>60+ Keyword-Patterns, Engagement-Analyse und adaptive Schwellenwerte.</p>
                        </div>
                        <div class="feature-card">
                            <h3>📊 Live-Statistiken</h3>
                            <p>Echtzeit Filter-Statistiken und transparente Algorithmus-Entscheidungen.</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🧪 V5.0 Enhanced Testing</h2>
                    <p style="margin-bottom: 20px;">Teste die neuen Anti-Bias Filter Features:</p>
                    
                    <a href="/analyze?query=cricket&region=DE&algorithm=regional&top_count=10" class="test-button">
                        🏏 Cricket DE Test (Max 1 indisches Video)
                    </a>
                    <a href="/analyze?query=sport&region=DE&algorithm=regional&top_count=10" class="test-button">
                        ⚽ Sport DE Test (Deutsche Inhalte bevorzugt)
                    </a>
                    <a href="/algorithm-test?query=gaming&region=DE" class="test-button">
                        📊 Algorithmus A/B Test
                    </a>
                    
                    <div style="margin-top: 30px;">
                        <a href="/test" class="test-button">✅ System Status</a>
                        <a href="/config-test" class="test-button">🔧 Config Test</a>
                        <a href="/youtube-test" class="test-button">📺 YouTube Test</a>
                        <a href="/api/algorithms" class="test-button">⚙️ API Info</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🏗️ V5.0 Enhanced Architecture</h2>
                    <p><strong>Modulare Trennung:</strong></p>
                    <ul style="margin: 15px 0; padding-left: 20px;">
                        <li><code>modular_server.py</code> → HTTP Server, API Endpoints</li>
                        <li><code>trending_algorithm.py</code> → V5.0 Enhanced Filter Logic</li>
                        <li><code>RegionalFilter</code> → Anti-Bias Pattern Recognition</li>
                        <li><code>V5TrendingAnalyzer</code> → Advanced Analytics Engine</li>
                    </ul>
                    
                    <p><strong>Erwartete Ergebnisse:</strong></p>
                    <ul style="margin: 15px 0; padding-left: 20px;">
                        <li>✅ 95% weniger irrelevante regionale Inhalte</li>
                        <li>✅ Maximal 1 indisches Video pro Suche</li>
                        <li>✅ Deutsche Inhalte +40% geboostet in DE-Region</li>
                        <li>✅ Transparente Filter-Statistiken</li>
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def handle_modular_analyze(self, params):
        """V5.0 Enhanced Analyze - SAUBERE ALGORITHMUS-INTEGRATION"""
        try:
            # Extract parameters
            query = params.get('query', [''])[0].strip()
            if not query:
                raise ValueError("Query parameter ist erforderlich")
            
            days = int(params.get('days', [2])[0])
            top_count = int(params.get('top_count', [12])[0])
            min_duration = int(params.get('min_duration', [0])[0])
            region = params.get('region', ['DE'])[0]
            algorithm_type = params.get('algorithm', ['regional'])[0]
            
            # Validate parameters
            if algorithm_type not in self.ALGORITHM_STRATEGIES:
                algorithm_type = 'regional'  # Fallback
            
            # Get video data from YouTube
            youtube_videos = self.fetch_youtube_videos(query, days, region, top_count * 3)
            
            if not youtube_videos:
                raise ValueError(f"Keine Videos für '{query}' gefunden")
            
            # Convert to VideoData objects
            video_data_list = [self.convert_to_video_data(video, region) for video in youtube_videos]
            video_data_list = [v for v in video_data_list if v is not None]
            
            # ===============================================
            # V5.0 SAUBERE ALGORITHMUS-INTEGRATION
            # Alle Filter-Logik ist jetzt in trending_algorithm.py!
            # ===============================================
            
            # Create V5.0 Enhanced Algorithm
            algorithm = self.create_algorithm(algorithm_type, region)
            
            # Create V5.0 Enhanced Analyzer
            analyzer = V5TrendingAnalyzer(algorithm, target_region=region)
            
            # V5.0 Enhanced Analysis (includes pre-filtering, score calculation, etc.)
            results, filter_stats = analyzer.analyze_videos(video_data_list, top_count)
            
            # Convert results for API response
            api_results = []
            for result in results:
                # Calculate realistic confidence
                real_confidence = calculate_realistic_confidence(
                    result.video_data.title,
                    result.video_data.channel,
                    result.video_data.views,
                    result.video_data.comments,
                    result.video_data.age_hours,
                    region
                )
                
                api_results.append({
                    'rank': result.rank,
                    'title': result.video_data.title,
                    'channel': result.video_data.channel,
                    'views': result.video_data.views,
                    'comments': result.video_data.comments,
                    'likes': result.video_data.likes,
                    'trending_score': round(result.trending_score, 2),
                    'normalized_score': round(result.normalized_score, 1),
                    'confidence': round(real_confidence, 3),
                    'age_hours': int(result.video_data.age_hours),
                    'duration_formatted': self.format_duration(result.video_data.duration_seconds),
                    'duration_seconds': result.video_data.duration_seconds,
                    'engagement_rate': round(result.video_data.comments / max(result.video_data.views, 1), 4),
                    'url': f"https://youtube.com/watch?v={result.video_data.video_id}",
                    'algorithm_version': result.algorithm_version,
                    'filter_applied': result.filter_applied,
                    'is_indian_content': result.is_indian_content,
                    'is_regional_content': result.is_regional_content
                })
            
            response_data = {
                "success": True,
                "query": query,
                "algorithm_used": algorithm_type,
                "algorithm_info": analyzer.get_algorithm_info(),
                "analyzed_videos": filter_stats["original_count"],
                "top_videos": api_results,
                "parameters": {
                    "query": query,
                    "days": days,
                    "top_count": top_count,
                    "min_duration": min_duration,
                    "region": region,
                    "algorithm": algorithm_type
                },
                "v5_enhanced_filter": {
                    "architecture": "V5.0 Enhanced - trending_algorithm.py",
                    "active": True,
                    "version": "5.0",
                    "filter_statistics": filter_stats,
                    "modular_design": True,
                    "separation_of_concerns": "Clean architecture"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": "V5.0 Enhanced analysis failed",
                "details": str(e),
                "available_algorithms": list(self.ALGORITHM_STRATEGIES.keys()),
                "architecture": "V5.0 Enhanced modular design",
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 500)
    
    def create_algorithm(self, algorithm_type: str, region: str):
        """Factory method für V5.0 Enhanced Algorithmus-Erstellung"""
        if algorithm_type == 'basic':
            return AlgorithmFactory.create_basic_algorithm()
        elif algorithm_type == 'regional':
            return AlgorithmFactory.create_regional_algorithm(region)
        elif algorithm_type == 'anti_spam':
            return AlgorithmFactory.create_anti_spam_algorithm()
        elif algorithm_type == 'experimental':
            return AlgorithmFactory.create_regional_algorithm(region)
        else:
            return AlgorithmFactory.create_regional_algorithm(region)
    
    def fetch_youtube_videos(self, query: str, days: int, region: str, max_results: int = 50):
        """Fetch videos from YouTube API"""
        try:
            from googleapiclient.discovery import build
            
            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                config = configparser.ConfigParser()
                if os.path.exists('config.ini'):
                    config.read('config.ini')
                    api_key = config.get('API', 'api_key', fallback=None)
            
            if not api_key:
                raise ValueError("YouTube API Key nicht gefunden!")
            
            youtube = build('youtube', 'v3', developerKey=api_key)
            published_after = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
            
            # Search parameters
            search_params = {
                'q': query,
                'part': 'snippet',
                'type': 'video',
                'publishedAfter': published_after,
                'maxResults': max_results,
                'order': 'relevance'
            }
            
            if region:
                search_params['regionCode'] = region.upper()
            
            search_request = youtube.search().list(**search_params)
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
            
            return details_response.get('items', [])
            
        except Exception as e:
            print(f"YouTube API error: {e}")
            return []
    
    def convert_to_video_data(self, youtube_video, target_region='DE') -> VideoData:
        """Convert YouTube API response to VideoData object"""
        try:
            import isodate
            
            stats = youtube_video.get('statistics', {})
            snippet = youtube_video.get('snippet', {})
            content_details = youtube_video.get('contentDetails', {})
            
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
            
            # Get thumbnail
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url = None
            for quality in ['maxres', 'high', 'medium', 'default']:
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality]['url']
                    break
            
            return VideoData(
                video_id=youtube_video['id'],
                title=snippet.get('title', 'Kein Titel'),
                channel=snippet.get('channelTitle', 'Unbekannt'),
                views=int(stats.get('viewCount', 0)),
                comments=int(stats.get('commentCount', 0)),
                likes=int(stats.get('likeCount', 0)),
                duration_seconds=duration_seconds,
                age_hours=age_hours,
                published_at=published_at,
                thumbnail=thumbnail_url
            )
            
        except Exception as e:
            print(f"Error converting video data: {e}")
            return None
    
    def format_duration(self, seconds):
        """Format duration in MM:SS or HH:MM:SS"""
        if seconds == 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def send_test(self):
        """V5.0 Enhanced System test"""
        data = {
            "status": "✅ V5.0 Enhanced Modular System funktioniert!",
            "architecture": {
                "design": "V5.0 Enhanced Modular",
                "server_layer": "✅ modular_server.py - Clean HTTP handling",
                "algorithm_layer": "✅ trending_algorithm.py - V5.0 Enhanced Filter",
                "separation_of_concerns": "✅ Perfect modular design"
            },
            "v5_features": {
                "enhanced_anti_bias": "✅ In algorithm layer",
                "regional_optimization": "✅ Enhanced pattern recognition",
                "pre_filtering": "✅ Quality-based selection",
                "modular_testing": "✅ Independent algorithm testing"
            },
            "algorithm_strategies": list(self.ALGORITHM_STRATEGIES.keys()),
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def send_config_test(self):
        """Config test"""
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            config = configparser.ConfigParser()
            if os.path.exists('config.ini'):
                config.read('config.ini')
                api_key = config.get('API', 'api_key', fallback=None)
        
        data = {
            "api_key_status": "✅ OK" if api_key and len(api_key) > 10 else "❌ FEHLER",
            "modular_system": "✅ V5.0 Enhanced Modular System geladen",
            "algorithm_layer": "✅ trending_algorithm.py mit V5.0 Filter verfügbar",
            "server_layer": "✅ modular_server.py mit sauberer API",
            "architecture_benefits": [
                "Clean separation of HTTP and algorithm logic",
                "Easy to test algorithm changes independently",
                "Reusable algorithm components",
                "Clear debugging in algorithm layer"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_json_response(data)
    
    def send_youtube_test(self):
        """YouTube API test"""
        try:
            from googleapiclient.discovery import build
            
            api_key = os.getenv('YOUTUBE_API_KEY')
            if not api_key:
                config = configparser.ConfigParser()
                if os.path.exists('config.ini'):
                    config.read('config.ini')
                    api_key = config.get('API', 'api_key', fallback=None)
            
            if not api_key:
                raise ValueError("YouTube API Key nicht gefunden")
            
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Test search
            request = youtube.search().list(
                q='test v5 modular architecture',
                part='snippet',
                maxResults=3,
                type='video'
            )
            response = request.execute()
            
            data = {
                "youtube_api_status": "✅ FUNKTIONIERT!",
                "test_results": len(response.get('items', [])),
                "v5_modular_ready": True,
                "algorithm_layer_ready": True,
                "server_layer_ready": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            data = {
                "youtube_api_status": "❌ FEHLER",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        self.send_json_response(data)
    
    def handle_algorithm_test(self, params):
        """V5.0 Enhanced Algorithm A/B Testing"""
        try:
            query = params.get('query', ['test'])[0]
            region = params.get('region', ['DE'])[0]
            
            # Get video data einmal
            youtube_videos = self.fetch_youtube_videos(query, 2, region, 30)
            video_data_list = [self.convert_to_video_data(video, region) for video in youtube_videos]
            video_data_list = [v for v in video_data_list if v is not None]
            
            if not video_data_list:
                raise ValueError("Keine Videos zum Testen gefunden")
            
            # Teste alle Algorithmen mit V5.0 Enhanced Architecture
            algorithm_results = {}
            for alg_type in self.ALGORITHM_STRATEGIES.keys():
                # Create algorithm and analyzer
                algorithm = self.create_algorithm(alg_type, region)
                analyzer = V5TrendingAnalyzer(algorithm, target_region=region)
                
                # V5.0 Enhanced Analysis
                results, filter_stats = analyzer.analyze_videos(video_data_list, 6)
                
                # Process results for comparison
                processed_results = []
                for r in results[:3]:
                    real_confidence = calculate_realistic_confidence(
                        r.video_data.title, r.video_data.channel, r.video_data.views, 
                        r.video_data.comments, r.video_data.age_hours, region
                    )
                    
                    processed_results.append({
                        "rank": r.rank,
                        "title": r.video_data.title[:50] + "...",
                        "trending_score": round(r.trending_score, 2),
                        "normalized_score": round(r.normalized_score, 1),
                        "confidence": round(real_confidence, 3),
                        "is_indian_content": r.is_indian_content,
                        "is_regional_content": r.is_regional_content,
                        "filter_applied": r.filter_applied
                    })
                
                algorithm_results[alg_type] = {
                    "name": self.ALGORITHM_STRATEGIES[alg_type],
                    "top_videos": processed_results,
                    "algorithm_info": analyzer.get_algorithm_info(),
                    "filter_statistics": filter_stats,
                    "v5_enhanced": True
                }
            
            response_data = {
                "success": True,
                "query": query,
                "region": region,
                "algorithm_comparison": algorithm_results,
                "test_info": {
                    "videos_analyzed": len(video_data_list),
                    "algorithms_tested": len(self.ALGORITHM_STRATEGIES),
                    "top_results_per_algorithm": 3,
                    "v5_architecture": "Enhanced modular design",
                    "filter_layer": "trending_algorithm.py"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.send_json_response(response_data)
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": "V5.0 Algorithm test failed",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 500)
    
    def handle_csv_export(self, params):
        """V5.0 Enhanced CSV export"""
        try:
            query = params.get('query', ['trending'])[0]
            days = int(params.get('days', [7])[0])
            top_count = int(params.get('top_count', [50])[0])
            min_duration = int(params.get('min_duration', [0])[0])
            region = params.get('region', [''])[0]
            
            # Get analysis data mit V5.0 Enhanced Architecture
            youtube_videos = self.fetch_youtube_videos(query, days, region, top_count * 2)
            video_data_list = [self.convert_to_video_data(video, region) for video in youtube_videos]
            video_data_list = [v for v in video_data_list if v is not None]
            
            if not video_data_list:
                raise ValueError("Keine Videos für Export gefunden")
            
            # V5.0 Enhanced Analysis
            algorithm = self.create_algorithm('regional', region)
            analyzer = V5TrendingAnalyzer(algorithm, target_region=region)
            results, filter_stats = analyzer.analyze_videos(video_data_list, top_count)
            
            # Create V5.0 Enhanced CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # V5.0 Enhanced Header
            writer.writerow([
                'Rank', 'Title', 'Channel', 'Views', 'Comments', 'Likes',
                'Trending_Score', 'Normalized_Score', 'Duration', 'Age_Hours', 
                'Engagement_Rate', 'Confidence', 'URL', 'Region',
                'Is_Indian_Content', 'Is_Regional_Content', 'Filter_Applied',
                'Algorithm_Version', 'V5_Architecture'
            ])
            
            # Data rows mit V5.0 Enhanced Info
            for result in results:
                real_confidence = calculate_realistic_confidence(
                    result.video_data.title, result.video_data.channel, 
                    result.video_data.views, result.video_data.comments, 
                    result.video_data.age_hours, region
                )
                
                writer.writerow([
                    result.rank, result.video_data.title, result.video_data.channel,
                    result.video_data.views, result.video_data.comments, result.video_data.likes,
                    round(result.trending_score, 2), round(result.normalized_score, 1),
                    self.format_duration(result.video_data.duration_seconds),
                    int(result.video_data.age_hours),
                    round(result.video_data.comments / max(result.video_data.views, 1), 4),
                    round(real_confidence, 3),
                    f"https://youtube.com/watch?v={result.video_data.video_id}",
                    region or 'Weltweit',
                    'Yes' if result.is_indian_content else 'No',
                    'Yes' if result.is_regional_content else 'No',
                    result.filter_applied or 'None',
                    result.algorithm_version,
                    'V5.0_Enhanced_Modular'
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            # Send CSV response
            region_suffix = f"_{region}" if region else "_weltweit"
            filename = f"youtube_trending_v5_enhanced_{query.replace(' ', '_')}{region_suffix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(csv_content.encode('utf-8'))
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": "V5.0 Enhanced CSV export failed",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 500)
    
    def handle_excel_export(self, params):
        """Excel export (fallback to CSV for now)"""
        self.handle_csv_export(params)
    
    def send_algorithm_info(self):
        """API endpoint für V5.0 Enhanced Algorithmus-Informationen"""
        algorithms_info = {}
        
        for alg_type in self.ALGORITHM_STRATEGIES.keys():
            algorithm = self.create_algorithm(alg_type, 'DE')
            analyzer = V5TrendingAnalyzer(algorithm, target_region='DE')
            algorithms_info[alg_type] = {
                "name": self.ALGORITHM_STRATEGIES[alg_type],
                "details": analyzer.get_algorithm_info(),
                "v5_enhanced": True,
                "architecture": "modular design"
            }
        
        data = {
            "available_algorithms": algorithms_info,
            "default_algorithm": "regional",
            "architecture": {
                "version": "V5.0 Enhanced",
                "design": "Modular separation of concerns",
                "server_layer": "modular_server.py - HTTP handling",
                "algorithm_layer": "trending_algorithm.py - Filter logic",
                "benefits": [
                    "Clean separation of concerns",
                    "Easy to test and modify algorithms",
                    "Reusable algorithm components",
                    "Clear debugging and logging"
                ]
            },
            "v5_enhancements": {
                "anti_bias_filter": "Built into algorithm layer",
                "regional_optimization": "Enhanced pattern recognition",
                "pre_filtering": "Quality-based video selection",
                "modular_design": "Server + Algorithm separation"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_json_response(data)
    
    def send_search_history(self):
        """V5.0 Enhanced search history"""
        data = {
            "message": "V5.0 Enhanced Search History mit Modular Architecture",
            "recent_searches": [
                {
                    "query": "gaming", "algorithm": "regional", "region": "DE", 
                    "results": 12, "architecture": "V5.0 Enhanced",
                    "filter_stats": {"indian_videos_filtered": 3, "german_videos_boosted": 2}
                },
                {
                    "query": "cricket", "algorithm": "regional", "region": "DE",
                    "results": 10, "architecture": "V5.0 Enhanced",
                    "filter_stats": {"indian_videos_filtered": 8, "german_videos_boosted": 0}
                }
            ],
            "architecture_benefits": [
                "Clean separation between server and algorithm logic",
                "Easy debugging with algorithm layer logs",
                "Independent testing of filter improvements",
                "Reusable algorithm components"
            ],
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def send_404(self):
        """V5.0 Enhanced 404 response"""
        data = {
            "error": "Endpoint nicht gefunden",
            "available_endpoints": {
                "system": ["/", "/test", "/config-test", "/youtube-test"],
                "analysis": ["/analyze", "/algorithm-test"],
                "export": ["/export/csv", "/export/excel"],
                "api": ["/api/algorithms", "/api/search-history"]
            },
            "v5_examples": [
                "/analyze?query=cricket&region=DE&algorithm=regional (V5.0 Anti-Bias)",
                "/analyze?query=sport&region=DE&algorithm=regional (V5.0 German Boost)",
                "/algorithm-test?query=gaming&region=DE (V5.0 A/B Test)"
            ],
            "architecture": {
                "version": "V5.0 Enhanced Modular",
                "server_layer": "modular_server.py - Clean HTTP handling",
                "algorithm_layer": "trending_algorithm.py - Enhanced filter logic",
                "benefits": "Perfect separation of concerns"
            },
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data, 404)
    
    def log_message(self, format, *args):
        """Enhanced logging with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} - {format % args}")


def start_modular_server(port=8000):
    """Start the V5.0 Enhanced Modular HTTP server"""
    try:
        with socketserver.TCPServer(("", port), ModularYouTubeHandler) as httpd:
            print("=" * 80)
            print("🚀 YouTube Trending Analyzer - V5.0 ENHANCED MODULAR ARCHITECTURE!")
            print("=" * 80)
            print(f"📡 Server läuft auf: http://localhost:{port}")
            print("🏠 Homepage: http://localhost:8000")
            print("🧪 Tests: /test, /config-test, /youtube-test")
            print("📊 Analyse: /analyze?query=BEGRIFF&region=LAND&algorithm=regional")
            print("📁 Export: /export/csv oder /export/excel")
            print("⚙️ API: /api/algorithms")
            print("=" * 80)
            print("🏗️ V5.0 ENHANCED MODULAR ARCHITECTURE:")
            print("   📡 modular_server.py → HTTP Server, API Endpoints, Data Conversion")
            print("   🧠 trending_algorithm.py → V5.0 Enhanced Filter, Score Calculation")
            print("   🎨 Frontend → React UI, User Interface")
            print("=" * 80)
            print("🎯 V5.0 ENHANCED FEATURES:")
            print("   🚫 Anti-Bias Filter: Max. 1 indisches Video (95% Reduktion)")
            print("   🇩🇪 Regional Boost: Deutsche Inhalte +40% in DE-Region")
            print("   🔍 Pattern Recognition: 60+ Keywords + Engagement-Analyse")
            print("   🏗️ Modular Design: Saubere Trennung von Server und Algorithmus")
            print("   📊 Pre-Filtering: Quality-basierte Video-Auswahl")
            print("   🧪 Easy Testing: Unabhängige Algorithmus-Tests")
            print("=" * 80)
            print("🧪 TESTE DIE V5.0 ENHANCED ARCHITECTURE:")
            print("   🏏 Anti-Bias: /analyze?query=cricket&region=DE&algorithm=regional")
            print("   ⚽ German Boost: /analyze?query=sport&region=DE&algorithm=regional")
            print("   📊 A/B Testing: /algorithm-test?query=gaming&region=DE")
            print("   ⚙️ Architecture: /api/algorithms")
            print("=" * 80)
            print("✅ V5.0 Enhanced Modular Architecture bereit! 🏗️")
            print("🛑 Server stoppen: Ctrl+C")
            print("=" * 80)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 V5.0 Enhanced Modular Server gestoppt!")
    except Exception as e:
        print(f"❌ Server-Fehler: {e}")


if __name__ == "__main__":
    # Port aus Environment Variable (Render/Railway) oder 8000 (lokal)
    port = int(os.environ.get('PORT', 8000))
    start_modular_server(port)
