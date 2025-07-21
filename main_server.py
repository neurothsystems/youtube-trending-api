# main_server_updated.py - V6.0 Server mit verbessertem Scraper
"""
V6.0 Server Update - Integration des verbesserten Trending Scrapers
"""

# In der V6TrendingAnalyzer Klasse, ersetze den Scraper-Import:

# ALTE VERSION (Zeile ~15):
# from core.trending_scraper import TrendingPageScraper, create_trending_scraper

# NEUE VERSION:
from core.trending_hybrid_v6 import DeployReadyHybridAnalyzer, create_trending_scraper

class V6TrendingAnalyzer:
    """V6.0 Main Analyzer mit verbessertem Scraper"""
    
    def __init__(self, 
                 target_region: str = "DE",
                 algorithm_config: Optional[Dict] = None,
                 filter_config: Optional[Dict] = None,
                 scraper_config: Optional[Dict] = None):
        """
        Initialize V6.0 Trending Analyzer mit verbessertem Scraper
        """
        self.target_region = target_region
        
        # Initialize components
        self.momentum_algorithm = create_momentum_algorithm(algorithm_config)
        self.regional_filter = create_regional_filter(target_region, filter_config)
        
        # 🔧 VERWENDE DEN VERBESSERTEN SCRAPER:
        self.trending_scraper = DeployReadyHybridAnalyzer()
        
        # Enhanced statistics
        self.analysis_stats = {
            'total_analyses': 0,
            'trending_page_videos': 0,
            'api_videos': 0,
            'filtered_videos': 0,
            'truly_trending_results': 0,
            'average_analysis_time': 0.0
        }
        
        print(f"🚀 V6.0 Analyzer mit IMPROVED SCRAPER für {target_region}")

    def analyze_trending_videos(self,
                               query: str,
                               region: Optional[str] = None,
                               top_count: int = 12,
                               use_trending_pages: bool = True,
                               trending_limit: int = 20,
                               api_limit: int = 30) -> Dict[str, Any]:
        """
        V6.0 Analyse mit verbessertem Scraper
        """
        start_time = time.time()
        region = region or self.target_region
        
        print(f"\n🚀 V6.0 IMPROVED ANALYSIS: '{query}' in {region}")
        print(f"📊 Mode: {'IMPROVED Trending Pages + API' if use_trending_pages else 'API Only'}")
        print("=" * 70)
        
        all_videos = []
        
        # Phase 1: IMPROVED Trending Pages (if enabled)
        if use_trending_pages:
            print("🔥 Phase 1: IMPROVED Trending Pages Scraping...")
            
            # ✅ VERWENDE DEN VERBESSERTEN SCRAPER:
            trending_videos, scrape_stats = self.trending_scraper.scrape_trending_videos(
                region=region, 
                keyword=query, 
                max_videos=trending_limit
            )
            
            print(f"🔥 Scraper Stats: {scrape_stats.videos_found} videos found")
            print(f"🔥 Success Rate: {scrape_stats.successful_scrapes}/{scrape_stats.total_requests}")
            
            # Enrich with API data
            if trending_videos:
                enriched_trending = self._enrich_videos_with_api(trending_videos)
                all_videos.extend(enriched_trending)
                print(f"✅ Trending Pages: {len(enriched_trending)} videos (IMPROVED)")
                
                # 🔍 DEBUG: Prüfe ob Videos als trending markiert sind
                trending_count = sum(1 for v in enriched_trending if v.is_trending_page_video)
                print(f"🔥 DEBUG: {trending_count}/{len(enriched_trending)} videos marked as trending")
            else:
                print("❌ IMPROVED Scraper found no videos - check scraper logs")
            
            self.analysis_stats['trending_page_videos'] = len(enriched_trending) if trending_videos else 0
        
        # Rest des Codes bleibt gleich...
        # (Phase 2: API, Phase 3: Deduplication, etc.)
        
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
        print(f"🔥 IMPROVED Truly Trending: {truly_trending}/{len(top_results)} videos")
        print(f"⏱️  Analysis Time: {analysis_time:.2f}s")
        print("=" * 70)
        
        # Build response mit IMPROVED Daten
        return {
            'success': True,
            'query': query,
            'region': region,
            'algorithm_used': 'momentum_v6.0_improved',
            'analysis_mode': 'V6.0 IMPROVED Trending Pages Enhanced' if use_trending_pages else 'V6.0 API Only',
            'analyzed_videos': len(unique_videos),
            'filtered_videos': len(filtered_videos),
            'top_videos': [self._result_to_dict(result) for result in top_results],
            'v6_statistics': {
                'trending_page_videos': self.analysis_stats['trending_page_videos'],
                'api_videos': self.analysis_stats['api_videos'],
                'truly_trending_in_results': truly_trending,
                'analysis_time_seconds': analysis_time,
                'deduplication_removed': len(all_videos) - len(unique_videos),
                'filter_removed': len(unique_videos) - len(filtered_videos),
                'scraper_version': 'V6.0 Improved'
            },
            'scraper_stats': self.trending_scraper.get_scraping_stats(),
            'filter_stats': filter_stats,
            'algorithm_info': self.momentum_algorithm.get_algorithm_info(),
            'timestamp': datetime.now().isoformat()
        }

    # Rest der Methoden bleibt gleich...
    # (Alle anderen Methoden wie _fetch_api_videos, _enrich_videos_with_api, etc.)


# ZUSÄTZLICHER FIX: Aktualisiere auch die Homepage
class V6HTTPHandler(http.server.BaseHTTPRequestHandler):
    """V6.0 HTTP Handler mit IMPROVED Scraper Info"""
    
    def send_homepage(self):
        """Send V6.0 homepage mit IMPROVED Info"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>YouTube Trending Analyzer V6.0 IMPROVED</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{ font-family: 'SF Pro Display', system-ui, sans-serif; margin: 0; padding: 20px; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; }}
                .container {{ max-width: 1000px; margin: 0 auto; }}
                .header {{ text-align: center; padding: 40px 0; }}
                .title {{ font-size: 3em; font-weight: 700; margin-bottom: 10px; }}
                .version {{ background: linear-gradient(45deg, #10b981, #059669); padding: 8px 16px; 
                           border-radius: 20px; font-size: 0.9em; margin-left: 15px; }}
                .improved {{ background: linear-gradient(45deg, #f59e0b, #d97706); padding: 8px 16px; 
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
                .improved-info {{ background: linear-gradient(45deg, #f59e0b, #d97706); color: white; 
                                 padding: 20px; border-radius: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 class="title">🚀 YouTube Trending Analyzer
                        <span class="version">V6.0</span>
                        <span class="improved">IMPROVED</span>
                    </h1>
                    <p class="subtitle">
                        IMPROVED Scraper + MOMENTUM Algorithm + Echte Trending-Seiten + Anti-Bias Filter
                    </p>
                    <p style="font-size: 0.9em; opacity: 0.8;">
                        🕐 Live seit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ⚡ IMPROVED Scraper
                    </p>
                </div>
                
                <div class="improved-info">
                    <h3>🔧 V6.0 IMPROVED Fixes:</h3>
                    <ul>
                        <li>✅ <strong>Multi-Method Scraping:</strong> 3 verschiedene Parsing-Methoden</li>
                        <li>✅ <strong>Anti-Detection:</strong> Verbesserte User-Agents und Headers</li>
                        <li>✅ <strong>Fallback-System:</strong> Alternative URLs wenn Hauptmethode faillt</li>
                        <li>✅ <strong>Robuste Extraktion:</strong> JSON + HTML + Legacy Support</li>
                        <li>✅ <strong>Better Debugging:</strong> Detaillierte Logs für Troubleshooting</li>
                    </ul>
                </div>
                
                <div class="features">
                    <div class="feature">
                        <h3>🔥 IMPROVED Trending-Scraper</h3>
                        <p>Scrapt direkt YouTube Trending-Seiten mit 3 Fallback-Methoden. 
                           Anti-Detection Maßnahmen und robuste Video-Extraktion für zuverlässige Ergebnisse.</p>
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
                        <h3>⚡ Improved Architecture</h3>
                        <p>V6.0 mit verbessertem Scraper. Fallback-Methoden, bessere Error-Handling, 
                           detaillierte Debug-Logs für optimale Trending-Erkennung.</p>
                    </div>
                </div>
                
                <div class="api-section">
                    <h2>🔧 V6.0 IMPROVED API Endpoints</h2>
                    
                    <h3>🎯 Haupt-Analyse (IMPROVED)</h3>
                    <div class="endpoint">
                        GET /analyze?query=BEGRIFF&region=LAND&trending_pages=true
                    </div>
                    <p><strong>Parameter:</strong> query (required), region (DE/US/GB/...), top_count (12), trending_pages (true/false), trending_limit (20), api_limit (30)</p>
                    
                    <h3>🧪 Testing (IMPROVED)</h3>
                    <div class="endpoint">
                        GET /trending-test?region=DE&keyword=gaming&max_videos=5
                    </div>
                    <div class="endpoint">
                        GET /health - System Health Check
                    </div>
                    <div class="endpoint">
                        GET /api/info - IMPROVED Algorithm & System Information
                    </div>
                    
                    <div class="test-links">
                        <a href="/analyze?query=gaming&region=DE&trending_pages=true&top_count=8" class="test-link">
                            🎮 Gaming DE (IMPROVED)
                        </a>
                        <a href="/analyze?query=musik&region=DE&trending_pages=true&top_count=8" class="test-link">
                            🎵 Musik DE (IMPROVED)
                        </a>
                        <a href="/analyze?query=sport&region=DE&trending_pages=true&top_count=8" class="test-link">
                            ⚽ Sport DE (IMPROVED)
                        </a>
                        <a href="/trending-test?region=DE&keyword=sport&max_videos=5" class="test-link">
                            🧪 IMPROVED Scraper Test
                        </a>
                        <a href="/health" class="test-link">
                            ✅ Health Check
                        </a>
                        <a href="/api/info" class="test-link">
                            ⚙️ IMPROVED API Info
                        </a>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px; opacity: 0.8; font-size: 0.9em;">
                    <p>🏗️ V6.0 IMPROVED Architecture - Robuste Trending-Erkennung</p>
                    <p>🚀 MOMENTUM Algorithm - Velocity-fokussierte Trend-Erkennung</p>
                    <p>🔥 IMPROVED Scraper - 3 Fallback-Methoden für maximale Zuverlässigkeit</p>
                    <p>⚡ Anti-Detection - User-Agent Rotation und intelligente Headers</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def handle_trending_test(self, params):
        """Test IMPROVED trending scraper directly"""
        try:
            region = params.get('region', ['DE'])[0].upper()
            keyword = params.get('keyword', [None])[0]
            max_videos = int(params.get('max_videos', [5])[0])
            
            # ✅ VERWENDE DEN IMPROVED SCRAPER:
            scraper = ImprovedTrendingPageScraper()
            videos, stats = scraper.scrape_trending_videos(region, keyword, max_videos)
            
            response = {
                'success': True,
                'test_type': 'V6.0 IMPROVED Trending Scraper',
                'region': region,
                'keyword': keyword,
                'videos_found': len(videos),
                'sample_videos': [
                    {
                        'video_id': v.video_id,
                        'title': v.title,
                        'channel': v.channel,
                        'source': v.source,
                        'is_trending_page_video': v.is_trending_page_video  # ✅ WICHTIG
                    } for v in videos[:3]
                ],
                'scraper_stats': scraper.get_scraping_stats(),
                'improvement_info': {
                    'version': 'V6.0 Improved',
                    'methods_used': 'Multi-method parsing with fallbacks',
                    'anti_detection': 'Enhanced user-agent rotation',
                    'success_indicators': 'is_trending_page_video=True for real trending videos'
                },
                'timestamp': datetime.now().isoformat()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': 'IMPROVED Trending scraper test failed',
                'details': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.send_json_response(error_response, 500)


# 🚀 START SERVER MIT IMPROVED SCRAPER
def start_v6_improved_server(port=8000):
    """Start V6.0 IMPROVED Server"""
    try:
        with socketserver.TCPServer(("", port), V6HTTPHandler) as httpd:
            print("=" * 80)
            print("🚀 YOUTUBE TRENDING ANALYZER V6.0 IMPROVED")
            print("=" * 80)
            print(f"📡 Server running: http://localhost:{port}")
            print(f"🏠 Homepage: http://localhost:{port}")
            print(f"🔧 Health: http://localhost:{port}/health")
            print(f"📊 API Info: http://localhost:{port}/api/info")
            print("=" * 80)
            print("🔧 V6.0 IMPROVED FIXES:")
            print("   🔥 Multi-Method Trending Scraper mit 3 Fallback-Strategien")
            print("   🛡️ Anti-Detection: User-Agent Rotation + Enhanced Headers")
            print("   🔄 Robuste Video-Extraktion: JSON + HTML + Legacy Support")
            print("   🧪 Improved Testing: Detaillierte Debug-Logs")
            print("   ⚡ Better Error Handling: Graceful Fallbacks")
            print("=" * 80)
            print("🎯 IMPROVED TESTS:")
            print(f"   🎮 Gaming: http://localhost:{port}/analyze?query=gaming&region=DE&trending_pages=true")
            print(f"   🎵 Musik: http://localhost:{port}/analyze?query=musik&region=DE&trending_pages=true")
            print(f"   🧪 Scraper: http://localhost:{port}/trending-test?region=DE&keyword=sport")
            print("=" * 80)
            print("✅ V6.0 IMPROVED Server ready! Press Ctrl+C to stop")
            print("=" * 80)
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 V6.0 IMPROVED Server stopped!")
    except Exception as e:
        print(f"❌ Server error: {e}")


if __name__ == "__main__":
    # Get port from environment or use 8000
    port = int(os.environ.get('PORT', 8000))
    start_v6_improved_server(port)
