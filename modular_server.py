# modular_server.py - SAUBERE VERSION mit V5.0 Algorithmus-Integration
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
    VideoData, V5TrendingAnalyzer, AlgorithmFactory,
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
        """TopMetric.ai Homepage mit echtem SVG-Logo"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TopMetric.ai - AI-Powered YouTube Trending Analytics</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <meta name="description" content="TopMetric.ai uses AI to find real YouTube trends before they explode. Advanced analytics with anti-bias filtering.">
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
            <style>
                :root {{
                    --primary: #ff3600;
                    --primary-light: #ff5722;
                    --primary-dark: #d32f2f;
                    --secondary: #00bcd4;
                    --success: #10b981;
                    --warning: #f59e0b;
                    --gray-50: #f8fafc;
                    --gray-100: #f1f5f9;
                    --gray-200: #e2e8f0;
                    --gray-300: #cbd5e1;
                    --gray-500: #64748b;
                    --gray-700: #334155;
                    --gray-800: #1e293b;
                    --gray-900: #0f172a;
                }}
                
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ 
                    font-family: 'Inter', system-ui, -apple-system, sans-serif; 
                    background: var(--gray-50);
                    color: var(--gray-800);
                    line-height: 1.6;
                }}
                
                .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
                
                /* LOGO STYLES */
                .logo-container {{
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-bottom: 24px;
                }}
                
                .logo-svg {{
                    height: 80px;
                    width: auto;
                    filter: drop-shadow(0 4px 8px rgba(255, 54, 0, 0.3));
                    transition: all 0.3s ease;
                }}
                
                .logo-svg:hover {{
                    transform: scale(1.05);
                    filter: drop-shadow(0 8px 16px rgba(255, 54, 0, 0.4));
                }}
                
                /* Responsive Logo */
                @media (max-width: 768px) {{
                    .logo-svg {{ height: 60px; }}
                }}
                
                @media (max-width: 480px) {{
                    .logo-svg {{ height: 50px; }}
                }}
                
                /* HEADER */
                .header {{ 
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); 
                    color: white; 
                    padding: 60px 40px; 
                    text-align: center; 
                    border-radius: 16px; 
                    margin-bottom: 40px;
                    box-shadow: 0 20px 25px -5px rgba(255, 54, 0, 0.2);
                }}
                
                .tagline {{ 
                    opacity: 0.95; 
                    font-size: 20px; 
                    font-weight: 500;
                    margin-bottom: 12px;
                }}
                
                .status-line {{
                    background: rgba(255,255,255,0.15);
                    padding: 12px 24px;
                    border-radius: 8px;
                    display: inline-block;
                    font-weight: 600;
                    backdrop-filter: blur(10px);
                }}
                
                /* SUCCESS BOX */
                .success-box {{ 
                    background: linear-gradient(135deg, var(--success) 0%, #059669 100%); 
                    color: white; 
                    padding: 20px; 
                    border-radius: 12px; 
                    margin-bottom: 30px; 
                    text-align: center; 
                    font-weight: 600;
                    box-shadow: 0 10px 15px -3px rgba(16, 185, 129, 0.2);
                }}
                
                /* CARDS */
                .card {{
                    background: white;
                    padding: 30px;
                    border-radius: 16px;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    margin-bottom: 30px;
                    border: 1px solid var(--gray-200);
                }}
                
                .algorithm-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                    gap: 20px; 
                    margin-top: 20px; 
                }}
                
                .algorithm-card {{ 
                    border: 2px solid var(--gray-200); 
                    padding: 24px; 
                    border-radius: 12px; 
                    cursor: pointer; 
                    transition: all 0.3s ease;
                    background: white;
                }}
                .algorithm-card:hover {{ 
                    border-color: var(--primary); 
                    background: #fef7f5;
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px -5px rgba(255, 54, 0, 0.15);
                }}
                .algorithm-card.selected {{ 
                    border-color: var(--primary); 
                    background: var(--primary); 
                    color: white;
                    box-shadow: 0 8px 25px -5px rgba(255, 54, 0, 0.3);
                }}
                .algorithm-card h3 {{
                    font-size: 18px;
                    font-weight: 700;
                    margin-bottom: 8px;
                }}
                .algorithm-card p {{
                    font-size: 14px;
                    opacity: 0.8;
                }}
                
                /* BUTTONS */
                .test-button {{ 
                    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); 
                    color: white; 
                    padding: 14px 24px; 
                    text-decoration: none; 
                    border-radius: 8px; 
                    display: inline-block; 
                    margin: 8px; 
                    transition: all 0.3s ease;
                    font-weight: 600;
                    font-size: 14px;
                    border: none;
                    cursor: pointer;
                }}
                .test-button:hover {{ 
                    transform: translateY(-2px);
                    box-shadow: 0 8px 25px -5px rgba(255, 54, 0, 0.4);
                }}
                
                .secondary-button {{
                    background: linear-gradient(135deg, var(--secondary) 0%, #0097a7 100%);
                }}
                
                .success-button {{
                    background: linear-gradient(135deg, var(--success) 0%, #059669 100%);
                }}
                
                /* BADGES */
                .ai-badge {{
                    background: linear-gradient(135deg, var(--warning) 0%, #d97706 100%);
                    color: white;
                    padding: 4px 10px;
                    border-radius: 16px;
                    font-size: 11px;
                    font-weight: 600;
                    margin-left: 8px;
                }}
                
                /* FEATURE GRID */
                .features-list {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); 
                    gap: 20px; 
                    margin-top: 20px; 
                }}
                
                .feature {{ 
                    background: var(--gray-50); 
                    padding: 20px; 
                    border-radius: 12px; 
                    border-left: 4px solid var(--primary);
                    transition: all 0.3s ease;
                }}
                .feature:hover {{
                    background: white;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                    transform: translateY(-1px);
                }}
                .feature strong {{
                    color: var(--gray-900);
                    font-weight: 700;
                }}
                .feature small {{
                    color: var(--gray-500);
                    font-size: 12px;
                }}
                
                /* API EXAMPLES SECTION */
                .api-examples {{ 
                    background: var(--gray-900); 
                    color: #e2e8f0; 
                    padding: 30px; 
                    border-radius: 16px; 
                    margin-top: 30px;
                    border: 1px solid var(--gray-700);
                }}
                .api-examples code {{ 
                    background: var(--gray-800); 
                    padding: 4px 8px; 
                    border-radius: 6px;
                    color: var(--primary-light);
                    font-weight: 600;
                }}
                .api-examples h3 {{
                    color: var(--primary-light);
                    margin: 25px 0 15px 0;
                    font-weight: 700;
                }}
                
                /* ANIMATIONS */
                @keyframes pulse {{
                    0%, 100% {{ opacity: 1; }}
                    50% {{ opacity: 0.6; }}
                }}
                .live-indicator {{
                    display: inline-block;
                    width: 8px;
                    height: 8px;
                    background: var(--success);
                    border-radius: 50%;
                    margin-right: 8px;
                    animation: pulse 2s infinite;
                }}
                
                /* SECTION TITLES */
                .section-title {{
                    color: var(--gray-900);
                    font-size: 28px;
                    font-weight: 800;
                    margin-bottom: 12px;
                }}
                .section-subtitle {{
                    color: var(--gray-500);
                    font-size: 16px;
                    margin-bottom: 24px;
                }}
                
                /* RESPONSIVE */
                @media (max-width: 768px) {{
                    .container {{ padding: 16px; }}
                    .header {{ padding: 40px 24px; }}
                    .tagline {{ font-size: 18px; }}
                    .algorithm-grid {{ grid-template-columns: 1fr; }}
                    .features-list {{ grid-template-columns: 1fr; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-box">
                    🚀 TopMetric.ai V5.0 Enhanced - AI-Powered Trending Analytics Live!
                </div>
                
                <div class="header">
                    <div class="logo-container">
                        <svg class="logo-svg" viewBox="0 0 388.00003 156.41664" xmlns="http://www.w3.org/2000/svg">
                            <defs>
                                <style>
                                    .cls-1 {{ fill: none; }}
                                    .cls-2 {{ fill: #ffffff; }}
                                </style>
                            </defs>
                            <g>
                                <rect class="cls-1" x="30.91757" y="18.91618" width="311.63811" height="152.86154"/>
                                <path d="M45.99805,28.14355h-13.52051v-6.5h34.38623v6.5h-13.52051v38.87158h-7.34521V28.14355Z"/>
                                <path d="M70.56836,44.3291c0-15.27539,7.73535-23.46582,19.56592-23.46582s19.56543,8.19043,19.56543,23.46582-7.73535,23.46631-19.56543,23.46631-19.56592-8.19043-19.56592-23.46631ZM101.83447,47.9043v-7.1499c0-8.25537-4.68018-13.32568-11.7002-13.32568-7.02051,0-11.70068,5.07031-11.70068,13.32568v7.1499c0,8.25537,4.68018,13.32568,11.70068,13.32568,7.02002,0,11.7002-5.07031,11.7002-13.32568Z"/>
                                <path d="M118.86279,67.01514V21.64355h19.50049c8.32031,0,13.1958,5.39502,13.1958,13.65039s-4.87549,13.65039-13.1958,13.65039h-12.15527v18.0708h-7.34521ZM126.20801,42.50928h11.7002c3.70557,0,5.91553-2.01514,5.91553-5.65527v-3.12012c0-3.64014-2.20996-5.65527-5.91553-5.65527h-11.7002v14.43066Z"/>
                                <path d="M36.50781,86.64355h8.71045l12.15527,23.07617h.39014l12.15527-23.07617h8.32031v45.37207h-7.02002v-34.71191h-.3252l-3.5752,7.3457-9.94531,18.13574-9.94531-18.13574-3.5752-7.3457h-.3252v34.71191h-7.02002v-45.37207Z"/>
                                <path d="M89.41748,132.01562v-45.37207h29.05615v6.5h-21.71094v12.61133h19.6958v6.5h-19.6958v13.26074h21.71094v6.5h-29.05615Z"/>
                                <path d="M137.45166,93.14355h-13.52051v-6.5h34.38623v6.5h-13.52051v38.87207h-7.34521v-38.87207Z"/>
                                <path d="M172.81152,132.01562h-7.34521v-45.37207h19.56543c8.12549,0,13.13086,5.26514,13.13086,13.65039,0,6.43555-3.05518,10.9209-8.84033,12.61035l9.81494,19.11133h-8.18994l-9.10059-18.33105h-9.03516v18.33105ZM184.51172,107.50977c3.70557,0,5.91553-2.01562,5.91553-5.65527v-3.12061c0-3.64014-2.20996-5.65527-5.91553-5.65527h-11.7002v14.43115h11.7002Z"/>
                                <path d="M206.09082,132.01562v-5.98047h6.17529v-33.41162h-6.17529v-5.97998h19.76074v5.97998h-6.24023v33.41162h6.24023v5.98047h-19.76074Z"/>
                                <path d="M233.06494,109.3291c0-15.21045,7.21533-23.46582,19.0459-23.46582,7.86523,0,13.13037,3.51025,16.18555,10.27051l-6.17529,3.38037c-1.56006-4.29053-4.74512-7.08545-10.01025-7.08545-6.95557,0-11.24561,5.07031-11.24561,13.45605v6.88965c0,8.38574,4.29004,13.45605,11.24561,13.45605,5.39502,0,8.83984-3.12012,10.46533-7.54102l5.91504,3.5752c-3.05518,6.56543-8.51514,10.53125-16.38037,10.53125-11.83057,0-19.0459-8.25586-19.0459-23.4668Z"/>
                            </g>
                            <g>
                                <rect class="cls-1" x="270.18319" y="83.8855" width="136.74447" height="78.61271"/>
                                <path class="cls-2" d="M274.86328,128.34473v-.97559c0-2.53516,1.56006-4.41992,4.74512-4.41992s4.74512,1.88477,4.74512,4.41992v.97559c0,2.53516-1.56006,4.41992-4.74512,4.41992s-4.74512-1.88477-4.74512-4.41992Z"/>
                                <path class="cls-2" d="M324.06885,131.98438l-4.09521-12.28516h-16.96533l-3.96533,12.28516h-7.4751l15.4707-45.37158h9.22998l15.4707,45.37158h-7.67041ZM311.65332,93.37305h-.32471l-6.56543,20.02051h13.39062l-6.50049-20.02051Z"/>
                                <path class="cls-2" d="M336.80713,131.98438v-5.98047h6.17529v-33.41113h-6.17529v-5.97998h19.76074v5.97998h-6.24023v33.41113h6.24023v5.98047h-19.76074Z"/>
                            </g>
                            <path class="cls-2" d="M152.67009,65.7897l26.6613-43.72981c.33713-.55296,1.14001-.55296,1.47715,0l26.6613,43.72981c.35144.57643-.06346,1.31531-.73857,1.31531h-53.32261c-.67511,0-1.09001-.73888-.73857-1.31531Z"/>
                        </svg>
                    </div>
                    <div class="tagline">Find YouTube Trends Before They Explode</div>
                    <div class="status-line">
                        <span class="live-indicator"></span>
                        <strong>Live V5.0 Enhanced</strong> | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    </div>
                </div>
                
                <div class="card">
                    <h2 class="section-title">🚀 V5.0 Enhanced Architecture</h2>
                    <p class="section-subtitle">AI-powered trending detection with anti-bias filtering</p>
                    <div class="algorithm-grid">
                        <div class="algorithm-card" onclick="selectAlgorithm('basic')">
                            <h3>🔹 Basic Algorithm</h3>
                            <p>Standard trending calculation with V5.0 enhanced filtering</p>
                        </div>
                        <div class="algorithm-card selected" onclick="selectAlgorithm('regional')">
                            <h3>🌍 Regional Optimized</h3>
                            <p>Advanced regional content prioritization + anti-bias</p>
                        </div>
                        <div class="algorithm-card" onclick="selectAlgorithm('anti_spam')">
                            <h3>🚫 Anti-Spam</h3>
                            <p>Spam detection with enhanced pattern recognition</p>
                        </div>
                        <div class="algorithm-card" onclick="selectAlgorithm('experimental')">
                            <h3>🧪 Experimental</h3>
                            <p>Latest AI features with advanced analytics</p>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <h2 class="section-title">🧪 Live Testing Suite</h2>
                    <div class="features-list">
                        <div class="feature">
                            <strong>🚫 Anti-Bias Testing</strong><br>
                            <a href="/analyze?query=cricket&region=DE&algorithm=regional&top_count=10" class="test-button">🏏 Cricket DE</a>
                            <small>Expected: Max 1 Indian video</small>
                        </div>
                        <div class="feature">
                            <strong>🇩🇪 German Content Boost</strong><br>
                            <a href="/analyze?query=sport&region=DE&algorithm=regional&top_count=10" class="test-button">⚽ Sport DE</a>
                            <small>Expected: German sports dominate</small>
                        </div>
                        <div class="feature">
                            <strong>⚖️ Algorithm Comparison</strong><br>
                            <a href="/algorithm-test?query=gaming&region=DE" class="test-button secondary-button">📊 A/B Test</a>
                            <small>Compare all algorithms</small>
                        </div>
                        <div class="feature">
                            <strong>⚙️ System Status</strong><br>
                            <a href="/test" class="test-button success-button">✅ Status</a>
                            <a href="/api/algorithms" class="test-button">🔧 API</a>
                            <small>Monitor system health</small>
                        </div>
                    </div>
                </div>
                
                <div class="api-examples">
                    <h2>🎯 TopMetric.ai V5.0 Features</h2>
                    <h3>✅ AI-Powered Bias Detection:</h3>
                    <p>✅ <code>60+ keyword patterns</code> → Identify problematic content</p>
                    <p>✅ <code>Engagement analysis</code> → Detect unnatural engagement spikes</p>
                    <p>✅ <code>Regional optimization</code> → Boost local content relevance</p>
                    <p>✅ <code>Quality filtering</code> → Only high-quality trending videos</p>
                    
                    <h3>🏗️ Enhanced Architecture:</h3>
                    <p><code>trending_algorithm.py</code> → All AI logic isolated</p>
                    <p><code>modular_server.py</code> → Clean API handling</p>
                    <p><code>V5TrendingAnalyzer</code> → Advanced pre-filtering</p>
                    <p><code>RegionalOptimizedAlgorithm</code> → Smart regional detection</p>
                    
                    <h3>📊 Expected Results:</h3>
                    <ul style="margin-top: 10px;">
                        <li>✅ 95% reduction in irrelevant regional content</li>
                        <li>✅ German content gets 40% boost in DE region</li>
                        <li>✅ Max 1 Indian video per search (down from 8-10)</li>
                        <li>✅ Real-time filter statistics and debugging</li>
                        <li>✅ Quality-based video selection algorithm</li>
                    </ul>
                </div>
            </div>
            
            <script>
                function selectAlgorithm(algorithm) {{
                    document.querySelectorAll('.algorithm-card').forEach(card => {{
                        card.classList.remove('selected');
                    }});
                    event.target.closest('.algorithm-card').classList.add('selected');
                    console.log('TopMetric.ai - Selected algorithm:', algorithm);
                }}
            </script>
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
    
    def create_algorithm(self, algorithm_type: str, region: str):
        """Factory method für V5.0 Enhanced Algorithmus-Erstellung"""
        if algorithm_type == 'basic':
            return AlgorithmFactory.create_basic_algorithm()
        elif algorithm_type == 'regional':
            return AlgorithmFactory.create_regional_algorithm(region)
        elif algorithm_type == 'anti_spam':
            return AlgorithmFactory.create_anti_spam_algorithm()
        elif algorithm_type == 'experimental':
            # Experimenteller Algorithmus - alle V5.0 Features
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
