# simple_server.py - Funktioniert IMMER (nur Standard Python Libraries)
import http.server
import socketserver
import json
import urllib.parse
from datetime import datetime, timedelta
import configparser
import math
import os

class YouTubeHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse URL
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        params = urllib.parse.parse_qs(parsed_url.query)
        
        # Route requests
        if path == '/':
            self.send_homepage()
        elif path == '/test':
            self.send_test()
        elif path == '/config-test':
            self.send_config_test()
        elif path == '/youtube-test':
            self.send_youtube_test()
        elif path == '/analyze':
            query = params.get('query', ['test'])[0]
            days = int(params.get('days', [2])[0])
            top_count = int(params.get('top_count', [5])[0])
            self.send_analyze(query, days, top_count)
        else:
            self.send_404()
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))
    
    def send_homepage(self):
        """Homepage with API documentation"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Trending Analyzer API</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .test-button { background: #007cba; color: white; padding: 10px 15px; text-decoration: none; border-radius: 3px; }
                h1 { color: #333; }
                h2 { color: #007cba; }
            </style>
        </head>
        <body>
            <h1>🎯 YouTube Trending Analyzer API</h1>
            <p><strong>Status:</strong> ✅ Server läuft erfolgreich!</p>
            <p><strong>Zeit:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            
            <h2>📋 Verfügbare Endpoints:</h2>
            
            <div class="endpoint">
                <h3>GET /test</h3>
                <p>Basis-Funktionstest</p>
                <a href="/test" class="test-button">Jetzt testen</a>
            </div>
            
            <div class="endpoint">
                <h3>GET /config-test</h3>
                <p>Prüft config.ini und API-Key</p>
                <a href="/config-test" class="test-button">Config testen</a>
            </div>
            
            <div class="endpoint">
                <h3>GET /youtube-test</h3>
                <p>Testet YouTube API Verbindung</p>
                <a href="/youtube-test" class="test-button">YouTube testen</a>
            </div>
            
            <div class="endpoint">
                <h3>GET /analyze?query=SUCHBEGRIFF</h3>
                <p>YouTube Trending Analyse</p>
                <a href="/analyze?query=ki&days=2&top_count=3" class="test-button">Beispiel: KI Suche</a>
            </div>
            
            <h2>🔧 Beispiel-URLs:</h2>
            <ul>
                <li><code>/analyze?query=künstliche intelligenz</code></li>
                <li><code>/analyze?query=python tutorial&days=7&top_count=10</code></li>
                <li><code>/analyze?query=musik 2024&days=1&top_count=5</code></li>
            </ul>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def send_test(self):
        """Simple test endpoint"""
        data = {
            "status": "✅ Server funktioniert perfekt!",
            "message": "HTTP Server mit Python Standard Library",
            "timestamp": datetime.now().isoformat(),
            "test_passed": True
        }
        self.send_json_response(data)
    
    def send_config_test(self):
        """Test configuration"""
        try:
            config = configparser.ConfigParser()
            config_exists = os.path.exists('config.ini')
            
            if config_exists:
                config.read('config.ini')
                api_key = config.get('API', 'api_key', fallback='NICHT_GEFUNDEN')
                key_status = "✅ OK" if api_key != 'NICHT_GEFUNDEN' and len(api_key) > 10 else "❌ FEHLER"
            else:
                api_key = "NICHT_GEFUNDEN"
                key_status = "❌ config.ini nicht gefunden"
            
            data = {
                "config_file_exists": config_exists,
                "api_key_status": key_status,
                "api_key_length": len(api_key) if api_key != 'NICHT_GEFUNDEN' else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            if not config_exists:
                data["help"] = "Erstellen Sie config.ini mit Ihrem YouTube API Key"
                
        except Exception as e:
            data = {"error": str(e), "timestamp": datetime.now().isoformat()}
        
        self.send_json_response(data)
    
    def send_youtube_test(self):
        """Test YouTube API connection"""
        try:
            # Import here to avoid startup errors
            from googleapiclient.discovery import build
            
            config = configparser.ConfigParser()
            config.read('config.ini')
            api_key = config.get('API', 'api_key')
            
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Simple test request
            request = youtube.search().list(
                q='test',
                part='snippet',
                maxResults=1,
                type='video'
            )
            response = request.execute()
            
            data = {
                "youtube_api_status": "✅ FUNKTIONIERT!",
                "test_results_found": len(response.get('items', [])),
                "quota_used": "~1 Einheit",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            data = {
                "youtube_api_status": "❌ FEHLER",
                "error": str(e),
                "help": "Prüfen Sie Ihren API-Key in config.ini",
                "timestamp": datetime.now().isoformat()
            }
        
        self.send_json_response(data)
    
    def send_analyze(self, query, days=2, top_count=5):
        """YouTube trending analysis"""
        try:
            # Import YouTube API
            from googleapiclient.discovery import build
            import isodate
            
            # Load config
            config = configparser.ConfigParser()
            config.read('config.ini')
            api_key = config.get('API', 'api_key')
            engagement_factor = config.getfloat('TRENDING', 'engagement_factor', fallback=10.0)
            freshness_exponent = config.getfloat('TRENDING', 'freshness_exponent', fallback=1.3)
            
            # Build YouTube service
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Time range
            published_after = (datetime.utcnow() - timedelta(days=days)).isoformat("T") + "Z"
            
            # Step 1: Search videos
            search_request = youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                publishedAfter=published_after,
                maxResults=20,
                order='viewCount'
            )
            search_response = search_request.execute()
            
            if not search_response.get('items'):
                data = {
                    "success": True,
                    "query": query,
                    "message": f"Keine Videos für '{query}' in den letzten {days} Tagen gefunden",
                    "videos": [],
                    "timestamp": datetime.now().isoformat()
                }
                self.send_json_response(data)
                return
            
            # Step 2: Get video details
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            details_request = youtube.videos().list(
                part='statistics,snippet,contentDetails',
                id=','.join(video_ids)
            )
            details_response = details_request.execute()
            
            # Step 3: Process videos
            videos = []
            for video in details_response.get('items', []):
                stats = video.get('statistics', {})
                snippet = video.get('snippet', {})
                
                views = int(stats.get('viewCount', 0))
                comments = int(stats.get('commentCount', 0))
                likes = int(stats.get('likeCount', 0))
                title = snippet.get('title', 'Kein Titel')
                channel = snippet.get('channelTitle', 'Unbekannt')
                published_at = snippet.get('publishedAt', '')
                
                # Calculate age
                try:
                    published = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
                    age_hours = max((datetime.utcnow() - published).total_seconds() / 3600, 1)
                except:
                    age_hours = 24  # fallback
                
                # Calculate trending score (your original algorithm)
                engagement_rate = comments / views if views > 0 else 0
                trending_score = (
                    (views + comments * engagement_factor)
                    / math.pow(age_hours, freshness_exponent)
                ) * (1 + engagement_rate)
                
                videos.append({
                    'title': title,
                    'channel': channel,
                    'views': views,
                    'comments': comments,
                    'likes': likes,
                    'trending_score': round(trending_score, 2),
                    'age_hours': int(age_hours),
                    'engagement_rate': round(engagement_rate, 4),
                    'url': f"https://youtube.com/watch?v={video['id']}"
                })
            
            # Sort by trending score
            videos.sort(key=lambda x: x['trending_score'], reverse=True)
            top_videos = videos[:top_count]
            
            # Add rankings
            for i, video in enumerate(top_videos, 1):
                video['rank'] = i
            
            data = {
                "success": True,
                "query": query,
                "search_days": days,
                "analyzed_videos": len(videos),
                "top_videos": top_videos,
                "algorithm": "Views + Comments * " + str(engagement_factor) + " / (age_hours ^ " + str(freshness_exponent) + ") * (1 + engagement_rate)",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            data = {
                "success": False,
                "query": query,
                "error": str(e),
                "help": "Prüfen Sie config.ini und YouTube API Key",
                "timestamp": datetime.now().isoformat()
            }
        
        self.send_json_response(data)
    
    def send_404(self):
        """404 Not Found"""
        data = {
            "error": "Endpoint nicht gefunden",
            "available_endpoints": ["/", "/test", "/config-test", "/youtube-test", "/analyze"],
            "example": "/analyze?query=test&days=2&top_count=5"
        }
        self.send_json_response(data, 404)
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {format % args}")

def start_server(port=8000):
    """Start the HTTP server"""
    try:
        with socketserver.TCPServer(("", port), YouTubeHandler) as httpd:
            print("=" * 60)
            print("🚀 YouTube Trending Analyzer Server")
            print("=" * 60)
            print(f"📡 Server läuft auf: http://localhost:{port}")
            print("🏠 Homepage: http://localhost:8000")
            print("🧪 Tests: http://localhost:8000/test")
            print("📊 Analyse: http://localhost:8000/analyze?query=test")
            print("=" * 60)
            print("✅ Server bereit! Öffnen Sie http://localhost:8000 im Browser")
            print("🛑 Server stoppen: Ctrl+C")
            print("=" * 60)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server gestoppt!")
    except Exception as e:
        print(f"❌ Server-Fehler: {e}")

if __name__ == "__main__":
    # Port aus Environment Variable (Render/Railway) oder 8000 (lokal)
    port = int(os.environ.get('PORT', 8000))
    start_server(port)
