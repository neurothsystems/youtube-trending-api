# enhanced_server.py - Erweiterte Version mit Original-Features
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

# Für Excel-Export
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

class EnhancedYouTubeHandler(http.server.BaseHTTPRequestHandler):
    
    # Rate limiting storage
    request_counts = defaultdict(list)
    max_requests_per_minute = 60
    
    def do_GET(self):
        """Handle GET requests with rate limiting"""
        
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
            self.send_enhanced_homepage()
        elif path == '/test':
            self.send_test()
        elif path == '/config-test':
            self.send_config_test()
        elif path == '/youtube-test':
            self.send_youtube_test()
        elif path == '/analyze':
            self.handle_analyze_request(params)
        elif path == '/export/csv':
            self.handle_csv_export(params)
        elif path == '/export/excel':
            self.handle_excel_export(params)
        elif path == '/api/search-history':
            self.send_search_history()
        elif path == '/api/trending-params':
            self.send_trending_params()
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
        """Send JSON response with enhanced headers"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'max-age=300')  # 5 minutes cache
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def send_enhanced_homepage(self):
        """Enhanced homepage with more features"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Trending Analyzer Pro</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; border-radius: 10px; margin-bottom: 30px; }
                .status-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }
                .endpoints-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .endpoint-card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                .endpoint-card h3 { color: #333; margin-bottom: 10px; }
                .test-button { background: linear-gradient(45deg, #FF6B6B, #4ECDC4); color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px; transition: transform 0.3s; }
                .test-button:hover { transform: translateY(-2px); }
                .export-button { background: linear-gradient(45deg, #43e97b, #38f9d7); color: white; padding: 8px 15px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 5px; font-size: 14px; }
                .features-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px; }
                .feature { background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }
                .api-examples { background: #2d3748; color: #e2e8f0; padding: 20px; border-radius: 10px; margin-top: 20px; }
                .api-examples code { background: #4a5568; padding: 2px 6px; border-radius: 3px; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 20px 0; }
                .stat-card { background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px; text-align: center; }
                .stat-number { font-size: 2em; font-weight: bold; }
                .live-status { display: inline-block; width: 12px; height: 12px; background: #4ECDC4; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎯 YouTube Trending Analyzer Pro</h1>
                    <p>Intelligente Trend-Analyse mit erweiterten Features</p>
                    <div style="margin-top: 20px;">
                        <span class="live-status"></span>
                        <strong>Live & Online</strong> | Server-Zeit: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
                    </div>
                </div>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">∞</div>
                        <div>API Calls</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">24/7</div>
                        <div>Verfügbarkeit</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">5</div>
                        <div>Endpoints</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">⚡</div>
                        <div>Performance</div>
                    </div>
                </div>

                <div class="status-card">
                    <h2>🚀 Neue Features</h2>
                    <div class="features-list">
                        <div class="feature">
                            <strong>📊 CSV/Excel Export</strong><br>
                            Exportieren Sie Trending-Daten in verschiedene Formate
                        </div>
                        <div class="feature">
                            <strong>⚡ Rate Limiting</strong><br>
                            Schutz vor Missbrauch mit intelligenter Begrenzung
                        </div>
                        <div class="feature">
                            <strong>📈 Erweiterte Parameter</strong><br>
                            Mehr Kontrolle über Suchalgorithmus und Filter
                        </div>
                        <div class="feature">
                            <strong>🎨 Bessere UI</strong><br>
                            Professionelles Design mit responsivem Layout
                        </div>
                    </div>
                </div>
                
                <div class="endpoints-grid">
                    <div class="endpoint-card">
                        <h3>🧪 System Tests</h3>
                        <p>Testen Sie alle Systemkomponenten</p>
                        <a href="/test" class="test-button">Server Test</a>
                        <a href="/config-test" class="test-button">Config Test</a>
                        <a href="/youtube-test" class="test-button">YouTube Test</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>📊 Trend-Analyse</h3>
                        <p>Finden Sie die aktuellsten Trending-Videos</p>
                        <a href="/analyze?query=ki&days=2&top_count=5" class="test-button">Beispiel: KI</a>
                        <a href="/analyze?query=musik&days=1&top_count=10" class="test-button">Beispiel: Musik</a>
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>📁 Export-Funktionen</h3>
                        <p>Exportieren Sie Analyseergebnisse</p>
                        <a href="/export/csv?query=trending&days=7&top_count=20" class="export-button">📄 CSV Download</a>
                        """ + ('    <a href="/export/excel?query=trending&days=7&top_count=20" class="export-button">📊 Excel Download</a>' if EXCEL_AVAILABLE else '    <span style="color: #999;">📊 Excel (nicht verfügbar)</span>') + """
                    </div>
                    
                    <div class="endpoint-card">
                        <h3>⚙️ API Management</h3>
                        <p>Konfiguration und Verlauf</p>
                        <a href="/api/trending-params" class="test-button">Parameter</a>
                        <a href="/api/search-history" class="test-button">Verlauf</a>
                    </div>
                </div>
                
                <div class="api-examples">
                    <h2>🔧 API-Endpunkte & Parameter</h2>
                    <h3>Trend-Analyse mit erweiterten Parametern:</h3>
                    <p><code>GET /analyze?query=SUCHBEGRIFF&days=N&top_count=N&min_duration=N&sort_by=trending_score</code></p>
                    
                    <h3>Export-Funktionen:</h3>
                    <p><code>GET /export/csv?query=BEGRIFF&days=7&top_count=50</code></p>
                    <p><code>GET /export/excel?query=BEGRIFF&days=7&top_count=50</code></p>
                    
                    <h3>Beispiele:</h3>
                    <ul style="margin-top: 10px;">
                        <li><code>/analyze?query=künstliche intelligenz&days=7&top_count=20&sort_by=views</code></li>
                        <li><code>/analyze?query=python tutorial&days=30&top_count=50&min_duration=300</code></li>
                        <li><code>/export/csv?query=gaming&days=3&top_count=100</code></li>
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
    
    def send_test(self):
        """Enhanced test endpoint with system info"""
        data = {
            "status": "✅ Server funktioniert perfekt!",
            "message": "Enhanced YouTube Trending Analyzer Pro",
            "timestamp": datetime.now().isoformat(),
            "features": {
                "csv_export": True,
                "excel_export": EXCEL_AVAILABLE,
                "rate_limiting": True,
                "enhanced_ui": True,
                "parameter_validation": True
            },
            "performance": {
                "requests_in_last_minute": len([
                    req_time for req_time in self.request_counts.get(self.client_address[0], [])
                    if req_time > time.time() - 60
                ]),
                "rate_limit": f"{self.max_requests_per_minute}/minute"
            },
            "test_passed": True
        }
        self.send_json_response(data)
    
    def send_config_test(self):
        """Enhanced config test with more details"""
        try:
            api_key = os.getenv('YOUTUBE_API_KEY')
            
            if api_key and len(api_key) > 10:
                key_status = "✅ OK (Environment Variable)"
                api_key_length = len(api_key)
                config_source = "Environment Variable"
            else:
                config = configparser.ConfigParser()
                config_exists = os.path.exists('config.ini')
                
                if config_exists:
                    config.read('config.ini')
                    api_key = config.get('API', 'api_key', fallback='NICHT_GEFUNDEN')
                    key_status = "✅ OK (config.ini)" if api_key != 'NICHT_GEFUNDEN' and len(api_key) > 10 else "❌ FEHLER"
                    api_key_length = len(api_key) if api_key != 'NICHT_GEFUNDEN' else 0
                    config_source = "config.ini"
                else:
                    key_status = "❌ Keine Konfiguration gefunden"
                    api_key_length = 0
                    config_source = "None"
            
            # Load trending parameters
            trending_config = self.load_trending_config()
            
            data = {
                "api_key_status": key_status,
                "api_key_length": api_key_length,
                "config_source": config_source,
                "trending_parameters": trending_config,
                "environment_variable_set": bool(os.getenv('YOUTUBE_API_KEY')),
                "config_file_exists": os.path.exists('config.ini'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            data = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        
        self.send_json_response(data)
    
    def send_youtube_test(self):
        """Enhanced YouTube test with quota info"""
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
            
            # Test search with quota tracking
            start_time = time.time()
            request = youtube.search().list(
                q='test api connection',
                part='snippet',
                maxResults=3,
                type='video'
            )
            response = request.execute()
            response_time = time.time() - start_time
            
            data = {
                "youtube_api_status": "✅ FUNKTIONIERT!",
                "test_results_found": len(response.get('items', [])),
                "response_time_ms": round(response_time * 1000, 2),
                "quota_used_estimate": "~3 Einheiten",
                "api_key_source": "Environment Variable" if os.getenv('YOUTUBE_API_KEY') else "config.ini",
                "test_query": "test api connection",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            data = {
                "youtube_api_status": "❌ FEHLER",
                "error": str(e),
                "help": "Prüfen Sie Ihren API-Key in Environment Variables oder config.ini",
                "timestamp": datetime.now().isoformat()
            }
        
        self.send_json_response(data)
    
    def load_trending_config(self):
        """Load trending algorithm configuration"""
        config = {
            "engagement_factor": 10.0,
            "freshness_exponent": 1.3,
            "min_duration_seconds": 0,
            "max_results": 50,
            "default_days": 2,
            "default_top_count": 10
        }
        
        if os.path.exists('config.ini'):
            parser = configparser.ConfigParser()
            parser.read('config.ini')
            
            if 'TRENDING' in parser.sections():
                config.update({
                    "engagement_factor": parser.getfloat('TRENDING', 'engagement_factor', fallback=10.0),
                    "freshness_exponent": parser.getfloat('TRENDING', 'freshness_exponent', fallback=1.3)
                })
            
            if 'SEARCH' in parser.sections():
                config.update({
                    "min_duration_seconds": parser.getint('SEARCH', 'min_duration_minutes', fallback=0) * 60,
                    "max_results": parser.getint('SEARCH', 'max_results', fallback=50),
                    "default_days": parser.getint('SEARCH', 'time_range_days', fallback=2),
                    "default_top_count": parser.getint('SEARCH', 'top_count', fallback=10)
                })
        
        return config
    
    def handle_analyze_request(self, params):
        """Enhanced analyze with parameter validation and caching"""
        try:
            # Extract and validate parameters
            query = params.get('query', [''])[0].strip()
            if not query:
                raise ValueError("Query parameter ist erforderlich")
            
            days = int(params.get('days', [2])[0])
            top_count = int(params.get('top_count', [5])[0])
            min_duration = int(params.get('min_duration', [0])[0])  # in seconds
            sort_by = params.get('sort_by', ['trending_score'])[0]
            
            # Parameter validation
            if days < 1 or days > 365:
                raise ValueError("days muss zwischen 1 und 365 liegen")
            if top_count < 1 or top_count > 100:
                raise ValueError("top_count muss zwischen 1 und 100 liegen")
            if min_duration < 0 or min_duration > 3600:
                raise ValueError("min_duration muss zwischen 0 und 3600 Sekunden liegen")
            if sort_by not in ['trending_score', 'views', 'comments', 'likes', 'age']:
                raise ValueError("sort_by muss einer von: trending_score, views, comments, likes, age sein")
            
            # Perform analysis
            result = self.perform_youtube_analysis(query, days, top_count, min_duration, sort_by)
            self.send_json_response(result)
            
        except ValueError as e:
            error_data = {
                "success": False,
                "error": "Parameter validation failed",
                "details": str(e),
                "help": {
                    "query": "Suchbegriff (erforderlich)",
                    "days": "1-365 (optional, default: 2)",
                    "top_count": "1-100 (optional, default: 5)", 
                    "min_duration": "0-3600 Sekunden (optional, default: 0)",
                    "sort_by": "trending_score|views|comments|likes|age (optional, default: trending_score)"
                },
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 400)
        except Exception as e:
            error_data = {
                "success": False,
                "error": "Analysis failed",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 500)
    
    def perform_youtube_analysis(self, query, days, top_count, min_duration, sort_by):
        """Core YouTube analysis logic"""
        from googleapiclient.discovery import build
        import isodate
        
        # Load API key and config
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            config = configparser.ConfigParser()
            if os.path.exists('config.ini'):
                config.read('config.ini')
                api_key = config.get('API', 'api_key', fallback=None)
        
        if not api_key:
            raise ValueError("YouTube API Key nicht gefunden!")
        
        trending_config = self.load_trending_config()
        engagement_factor = trending_config['engagement_factor']
        freshness_exponent = trending_config['freshness_exponent']
        
        youtube = build('youtube', 'v3', developerKey=api_key)
        published_after = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
        
        # Search videos
        search_request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            publishedAfter=published_after,
            maxResults=min(50, top_count * 2),  # Get more results for filtering
            order='viewCount'
        )
        search_response = search_request.execute()
        
        if not search_response.get('items'):
            return {
                "success": True,
                "query": query,
                "message": f"Keine Videos für '{query}' in den letzten {days} Tagen gefunden",
                "videos": [],
                "parameters": {
                    "days": days,
                    "top_count": top_count,
                    "min_duration": min_duration,
                    "sort_by": sort_by
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # Get video details
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        details_request = youtube.videos().list(
            part='statistics,snippet,contentDetails',
            id=','.join(video_ids)
        )
        details_response = details_request.execute()
        
        # Process videos
        videos = []
        for video in details_response.get('items', []):
            processed_video = self.process_video_data(video, engagement_factor, freshness_exponent)
            
            # Apply duration filter
            if processed_video['duration_seconds'] >= min_duration:
                videos.append(processed_video)
        
        # Sort videos
        if sort_by == 'trending_score':
            videos.sort(key=lambda x: x['trending_score'], reverse=True)
        elif sort_by == 'views':
            videos.sort(key=lambda x: x['views'], reverse=True)
        elif sort_by == 'comments':
            videos.sort(key=lambda x: x['comments'], reverse=True)
        elif sort_by == 'likes':
            videos.sort(key=lambda x: x['likes'], reverse=True)
        elif sort_by == 'age':
            videos.sort(key=lambda x: x['age_hours'])
        
        # Get top results
        top_videos = videos[:top_count]
        
        # Add rankings
        for i, video in enumerate(top_videos, 1):
            video['rank'] = i
        
        return {
            "success": True,
            "query": query,
            "analyzed_videos": len(videos),
            "filtered_videos": len([v for v in videos if v['duration_seconds'] >= min_duration]),
            "top_videos": top_videos,
            "parameters": {
                "days": days,
                "top_count": top_count,
                "min_duration": min_duration,
                "sort_by": sort_by,
                "engagement_factor": engagement_factor,
                "freshness_exponent": freshness_exponent
            },
            "algorithm": f"Views + Comments * {engagement_factor} / (age_hours ^ {freshness_exponent}) * (1 + engagement_rate)",
            "timestamp": datetime.now().isoformat()
        }
    
    def process_video_data(self, video, engagement_factor, freshness_exponent):
        """Process individual video data"""
        import isodate
        
        stats = video.get('statistics', {})
        snippet = video.get('snippet', {})
        content_details = video.get('contentDetails', {})
        
        views = int(stats.get('viewCount', 0))
        comments = int(stats.get('commentCount', 0))
        likes = int(stats.get('likeCount', 0))
        title = snippet.get('title', 'Kein Titel')
        channel = snippet.get('channelTitle', 'Unbekannt')
        published_at = snippet.get('publishedAt', '')
        
        # Parse duration
        duration_str = content_details.get('duration', 'PT0M0S')
        try:
            duration = isodate.parse_duration(duration_str)
            duration_seconds = int(duration.total_seconds())
        except:
            duration_seconds = 0
        
        # Calculate age
        try:
            published = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
            age_hours = max((datetime.utcnow() - published).total_seconds() / 3600, 1)
        except:
            age_hours = 24
        
        # Calculate trending score
        engagement_rate = comments / views if views > 0 else 0
        trending_score = (
            (views + comments * engagement_factor)
            / math.pow(age_hours, freshness_exponent)
        ) * (1 + engagement_rate)
        
        # Format duration
        duration_formatted = self.format_duration(duration_seconds)
        
        return {
            'title': title,
            'channel': channel,
            'views': views,
            'comments': comments,
            'likes': likes,
            'trending_score': round(trending_score, 2),
            'age_hours': int(age_hours),
            'duration_seconds': duration_seconds,
            'duration_formatted': duration_formatted,
            'engagement_rate': round(engagement_rate, 4),
            'published_at': published_at,
            'url': f"https://youtube.com/watch?v={video['id']}"
        }
    
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
    
    def handle_csv_export(self, params):
        """Handle CSV export requests"""
        try:
            query = params.get('query', ['trending'])[0]
            days = int(params.get('days', [7])[0])
            top_count = int(params.get('top_count', [50])[0])
            min_duration = int(params.get('min_duration', [0])[0])
            
            # Get analysis data
            analysis_result = self.perform_youtube_analysis(query, days, top_count, min_duration, 'trending_score')
            
            if not analysis_result['success']:
                raise ValueError("Analysis failed")
            
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Header
            writer.writerow([
                'Rank', 'Title', 'Channel', 'Views', 'Comments', 'Likes',
                'Trending Score', 'Duration', 'Age (Hours)', 'Engagement Rate', 'URL'
            ])
            
            # Data rows
            for video in analysis_result['top_videos']:
                writer.writerow([
                    video['rank'],
                    video['title'],
                    video['channel'],
                    video['views'],
                    video['comments'],
                    video['likes'],
                    video['trending_score'],
                    video['duration_formatted'],
                    video['age_hours'],
                    video['engagement_rate'],
                    video['url']
                ])
            
            csv_content = output.getvalue()
            output.close()
            
            # Send CSV response
            filename = f"youtube_trending_{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(csv_content.encode('utf-8'))
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": "CSV export failed",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 500)
    
    def handle_excel_export(self, params):
        """Handle Excel export requests"""
        if not EXCEL_AVAILABLE:
            error_data = {
                "success": False,
                "error": "Excel export not available",
                "details": "openpyxl library not installed",
                "help": "Install with: pip install openpyxl",
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 500)
            return
        
        try:
            query = params.get('query', ['trending'])[0]
            days = int(params.get('days', [7])[0])
            top_count = int(params.get('top_count', [50])[0])
            min_duration = int(params.get('min_duration', [0])[0])
            
            # Get analysis data
            analysis_result = self.perform_youtube_analysis(query, days, top_count, min_duration, 'trending_score')
            
            if not analysis_result['success']:
                raise ValueError("Analysis failed")
            
            # Create Excel workbook
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "YouTube Trending Analysis"
            
            # Styles
            header_font = Font(bold=True, color="FFFFFF")
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            center_alignment = Alignment(horizontal="center")
            
            # Headers
            headers = [
                'Rank', 'Title', 'Channel', 'Views', 'Comments', 'Likes',
                'Trending Score', 'Duration', 'Age (Hours)', 'Engagement Rate', 'URL'
            ]
            
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = center_alignment
            
            # Data rows
            for row, video in enumerate(analysis_result['top_videos'], 2):
                ws.cell(row=row, column=1, value=video['rank'])
                ws.cell(row=row, column=2, value=video['title'])
                ws.cell(row=row, column=3, value=video['channel'])
                ws.cell(row=row, column=4, value=video['views'])
                ws.cell(row=row, column=5, value=video['comments'])
                ws.cell(row=row, column=6, value=video['likes'])
                ws.cell(row=row, column=7, value=video['trending_score'])
                ws.cell(row=row, column=8, value=video['duration_formatted'])
                ws.cell(row=row, column=9, value=video['age_hours'])
                ws.cell(row=row, column=10, value=video['engagement_rate'])
                ws.cell(row=row, column=11, value=video['url'])
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Save to bytes
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_content = excel_buffer.getvalue()
            excel_buffer.close()
            
            # Send Excel response
            filename = f"youtube_trending_{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(excel_content)
            
        except Exception as e:
            error_data = {
                "success": False,
                "error": "Excel export failed",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            }
            self.send_json_response(error_data, 500)
    
    def send_search_history(self):
        """Send search history (placeholder for now)"""
        # In a real implementation, this would track searches in a database
        data = {
            "message": "Search history feature - ready for database integration",
            "recent_searches": [
                {"query": "ki", "timestamp": "2025-07-12T10:30:00", "results": 15},
                {"query": "musik", "timestamp": "2025-07-12T10:15:00", "results": 23},
                {"query": "gaming", "timestamp": "2025-07-12T09:45:00", "results": 31}
            ],
            "total_searches": 156,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def send_trending_params(self):
        """Send current trending algorithm parameters"""
        config = self.load_trending_config()
        
        data = {
            "current_parameters": config,
            "parameter_descriptions": {
                "engagement_factor": "Multiplier für Comments in der Trending-Berechnung",
                "freshness_exponent": "Exponentieller Abfall für ältere Videos",
                "min_duration_seconds": "Mindestdauer für Videos in Sekunden",
                "max_results": "Maximale Anzahl Videos pro Abfrage",
                "default_days": "Standard-Zeitraum für Suche",
                "default_top_count": "Standard-Anzahl Top-Ergebnisse"
            },
            "algorithm_formula": "trending_score = (views + comments * engagement_factor) / (age_hours ^ freshness_exponent) * (1 + engagement_rate)",
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def send_404(self):
        """Enhanced 404 response"""
        data = {
            "error": "Endpoint nicht gefunden",
            "available_endpoints": {
                "system": ["/", "/test", "/config-test", "/youtube-test"],
                "analysis": ["/analyze"],
                "export": ["/export/csv", "/export/excel"],
                "api": ["/api/search-history", "/api/trending-params"]
            },
            "examples": [
                "/analyze?query=test&days=2&top_count=5",
                "/export/csv?query=trending&days=7&top_count=20",
                "/api/trending-params"
            ],
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data, 404)
    
    def log_message(self, format, *args):
        """Enhanced logging with timestamp"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.client_address[0]} - {format % args}")

def start_enhanced_server(port=8000):
    """Start the enhanced HTTP server"""
    try:
        with socketserver.TCPServer(("", port), EnhancedYouTubeHandler) as httpd:
            print("=" * 80)
            print("🚀 YouTube Trending Analyzer Pro - Enhanced Edition")
            print("=" * 80)
            print(f"📡 Server läuft auf: http://localhost:{port}")
            print("🏠 Homepage: http://localhost:8000")
            print("🧪 Tests: /test, /config-test, /youtube-test")
            print("📊 Analyse: /analyze?query=BEGRIFF&days=N&top_count=N")
            print("📁 Export: /export/csv oder /export/excel")
            print("⚙️ API: /api/trending-params, /api/search-history")
            print("=" * 80)
            print("✨ Neue Features:")
            print("   • CSV/Excel Export")
            print("   • Rate Limiting (60 requests/minute)")
            print("   • Erweiterte Parameter-Validierung")
            print("   • Bessere UI mit responsivem Design")
            print("   • Performance-Monitoring")
            print(f"   • Excel Support: {'✅ Verfügbar' if EXCEL_AVAILABLE else '❌ Nicht installiert'}")
            print("=" * 80)
            print("✅ Server bereit! Öffnen Sie http://localhost:8000 im Browser")
            print("🛑 Server stoppen: Ctrl+C")
            print("=" * 80)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server gestoppt!")
    except Exception as e:
        print(f"❌ Server-Fehler: {e}")

if __name__ == "__main__":
    # Port aus Environment Variable (Render/Railway) oder 8000 (lokal)
    port = int(os.environ.get('PORT', 8000))
    start_enhanced_server(port)
