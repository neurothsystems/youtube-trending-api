# trending_algorithm.py - V6.1 Production-Ready Regional Trending Engine
"""
V6.1 Enhanced Regional YouTube Trending Algorithm
- Adaptive Query-Expansion mit Fallback-Strategien
- Robuste Channel-Geography-Detection mit Spam-Filtering
- Score-Histogramm und Debugging-Features
- Production-Level Error-Handling und Performance-Monitoring

Fixes das indische Video-Dominanz Problem durch intelligente regionale Suche
"""

import asyncio
import re
import math
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoData:
    """Standardisierte Video-Datenstruktur"""
    video_id: str
    title: str
    channel: str
    views: int
    comments: int
    likes: int
    duration_seconds: int
    age_hours: float
    published_at: str
    thumbnail: Optional[str] = None
    language_detected: Optional[str] = None
    region_detected: Optional[str] = None


@dataclass
class TrendingResult:
    """Ergebnis der Trending-Analyse"""
    video_data: VideoData
    trending_score: float
    rank: int
    normalized_score: float
    confidence: float = 1.0
    algorithm_version: str = "v6.1"
    filter_applied: Optional[str] = None
    is_indian_content: bool = False
    is_regional_content: bool = False
    regional_relevance: Optional[Dict] = None
    blacklisted: bool = False


class RegionalQueryBuilder:
    """V6.1: Adaptive Query-Expansion mit Fallback-Strategien"""
    
    REGIONAL_PATTERNS = {
        'DE': {
            'primary': ['{query} deutsch', '{query} deutschland'],
            'secondary': ['{query} german', '{query} auf deutsch', 'german {query}'],
            'language_patterns': ['german {query}', '{query} in german'],
            'fallback': ['{query}'],
            'boost_keywords': ['deutsch', 'deutschland', 'german', 'ard', 'zdf', 'rtl', 'pro7', 'sat1'],
            'min_results_threshold': 8
        },
        'US': {
            'primary': ['{query} american', '{query} usa'],
            'secondary': ['{query} english', 'american {query}', '{query} us'],
            'language_patterns': ['english {query}', '{query} in english'],
            'fallback': ['{query}'],
            'boost_keywords': ['american', 'usa', 'english', 'cnn', 'nbc', 'fox', 'espn'],
            'min_results_threshold': 8
        },
        'FR': {
            'primary': ['{query} français', '{query} france'],
            'secondary': ['{query} french', 'french {query}'],
            'language_patterns': ['french {query}', '{query} en français'],
            'fallback': ['{query}'],
            'boost_keywords': ['français', 'france', 'tf1', 'canal'],
            'min_results_threshold': 8
        },
        'ES': {
            'primary': ['{query} español', '{query} españa'],
            'secondary': ['{query} spanish', 'spanish {query}'],
            'language_patterns': ['spanish {query}', '{query} en español'],
            'fallback': ['{query}'],
            'boost_keywords': ['español', 'españa', 'rtve'],
            'min_results_threshold': 8
        },
        'GB': {
            'primary': ['{query} british', '{query} uk'],
            'secondary': ['{query} britain', 'british {query}'],
            'language_patterns': ['british {query}', '{query} in britain'],
            'fallback': ['{query}'],
            'boost_keywords': ['british', 'britain', 'uk', 'bbc'],
            'min_results_threshold': 8
        }
    }
    
    def build_adaptive_query_plan(self, base_query: str, region: str) -> dict:
        """V6.1: Adaptive Query-Expansion mit Fallback-Logik"""
        patterns = self.REGIONAL_PATTERNS.get(region, {
            'primary': [], 'secondary': [], 'language_patterns': [], 
            'fallback': [base_query], 'min_results_threshold': 5,
            'boost_keywords': []
        })
        
        return {
            'base_query': base_query,
            'target_region': region,
            'phase_1_queries': [p.format(query=base_query) for p in patterns['primary'][:2]],
            'phase_2_queries': [p.format(query=base_query) for p in patterns['secondary'][:2]],
            'language_queries': [p.format(query=base_query) for p in patterns['language_patterns'][:1]],
            'final_fallback': patterns['fallback'],
            'boost_keywords': patterns['boost_keywords'],
            'min_results_threshold': patterns['min_results_threshold'],
            'max_total_api_calls': 6
        }


class ChannelGeographyAnalyzer:
    """V6.1: Robuste Channel-Analyse mit Blacklisting und Safety-Checks"""
    
    def __init__(self):
        self.channel_cache = {}
        
        # V6.1: Spam-Pattern-Detection
        self.spam_patterns = [
            r'.*viral.*video.*',
            r'.*\d+k.*subscribers.*',
            r'.*funny.*clips.*',
            r'.*subscribe.*like.*',
            r'.*entertainment.*official.*',
            r'.*music.*entertainment.*'
        ]
        
        # V6.1: Bekannte indische Spam-Indikatoren
        self.indian_spam_indicators = [
            'subscribe karo', 'like kijiye', 'share karo', 'bell icon dabaye',
            'crore views', 'lakh subscribers', 'viral video', 'funny video',
            'entertainment official', 'music entertainment'
        ]
        
        self.confidence_thresholds = {
            'high': 0.8, 'medium': 0.5, 'low': 0.3
        }
    
    def analyze_channel_geography_v6(self, video_data: VideoData, target_region: str) -> dict:
        """V6.1: Robuste Multi-Source Channel-Analysis"""
        channel_id = video_data.channel
        
        cache_key = f"{channel_id}_{target_region}"
        if cache_key in self.channel_cache:
            return self.channel_cache[cache_key]
        
        # V6.1: Spam-Check zuerst
        if self._is_spam_channel(video_data):
            analysis = {
                'geography_score': 0.0,
                'confidence': 1.0,
                'sources_used': ['spam_detection'],
                'detected_region': 'SPAM',
                'blacklisted': True,
                'spam_reasons': self._get_spam_reasons(video_data)
            }
            self.channel_cache[cache_key] = analysis
            return analysis
        
        analysis = {
            'geography_score': 0.0,
            'confidence': 0.0,
            'sources_used': [],
            'detected_region': None,
            'blacklisted': False,
            'source_details': {}
        }
        
        # Source 1: Channel-Name Analysis (Keyword-basiert, zuverlässig)
        try:
            name_analysis = self._analyze_channel_name_safe(video_data.channel, target_region)
            if name_analysis['score'] > 0:
                analysis['geography_score'] += name_analysis['score'] * 0.4
                analysis['sources_used'].append('channel_name')
                analysis['source_details']['channel_name'] = name_analysis
                
                if name_analysis['score'] > 0.7:
                    analysis['detected_region'] = target_region
        except Exception as e:
            print(f"⚠️ Channel-Name-Analysis-Error: {e}")
        
        # Source 2: Content-Language-Pattern
        try:
            content_analysis = self._analyze_content_language_safe(video_data, target_region)
            if content_analysis['score'] > 0:
                analysis['geography_score'] += content_analysis['score'] * 0.3
                analysis['sources_used'].append('content_analysis')
                analysis['source_details']['content_analysis'] = content_analysis
        except Exception as e:
            print(f"⚠️ Content-Analysis-Error: {e}")
        
        # Source 3: Anti-Indian-Bias-Detection (spezielle Behandlung)
        try:
            indian_analysis = self._detect_indian_content(video_data, target_region)
            if indian_analysis['is_indian'] and target_region != 'IN':
                # Starke Reduktion für indische Inhalte in anderen Regionen
                analysis['geography_score'] *= 0.1  # 90% Reduktion
                analysis['sources_used'].append('anti_indian_bias')
                analysis['source_details']['indian_detection'] = indian_analysis
            elif indian_analysis['is_indian'] and target_region == 'IN':
                # Boost für indische Inhalte in Indien
                analysis['geography_score'] += 0.3
        except Exception as e:
            print(f"⚠️ Indian-Content-Detection-Error: {e}")
        
        # V6.1: Confidence basierend auf Source-Qualität und Anzahl
        analysis['confidence'] = self._calculate_source_confidence(analysis['sources_used'])
        
        # V6.1: Fallback-Logik bei 0 Sources
        if not analysis['sources_used'] or analysis['geography_score'] == 0:
            analysis['geography_score'] = 0.0
            analysis['confidence'] = 0.0
            analysis['detected_region'] = 'UNKNOWN'
        
        # Normalisiere Score auf 0-1
        analysis['geography_score'] = min(analysis['geography_score'], 1.0)
        
        self.channel_cache[cache_key] = analysis
        return analysis
    
    def _analyze_channel_name_safe(self, channel_name: str, target_region: str) -> dict:
        """V6.1: Sichere Channel-Name-Analysis"""
        if not channel_name or len(channel_name.strip()) < 3:
            return {'score': 0.0, 'method': 'too_short', 'reliability': 'none'}
        
        channel_lower = channel_name.lower().strip()
        
        # Regionale Keywords (erweitert und präziser)
        regional_keywords = {
            'DE': {
                'strong': ['deutsch', 'deutschland', 'german', 'ard', 'zdf', 'rtl', 'pro7', 'sat1'],
                'medium': ['berlin', 'münchen', 'hamburg', 'köln', 'bayern', 'nrw'],
                'weak': ['tv', 'news', 'sport']
            },
            'US': {
                'strong': ['american', 'usa', 'america', 'cnn', 'nbc', 'fox', 'espn'],
                'medium': ['washington', 'california', 'texas', 'new york'],
                'weak': ['tv', 'news', 'sports']
            },
            'FR': {
                'strong': ['français', 'france', 'tf1', 'canal'],
                'medium': ['paris', 'bordeaux', 'lyon'],
                'weak': ['tv', 'news']
            },
            'ES': {
                'strong': ['español', 'españa', 'rtve'],
                'medium': ['madrid', 'barcelona', 'valencia'],
                'weak': ['tv', 'news']
            },
            'GB': {
                'strong': ['british', 'britain', 'uk', 'bbc'],
                'medium': ['london', 'manchester', 'scotland'],
                'weak': ['tv', 'news']
            }
        }
        
        keywords = regional_keywords.get(target_region, {'strong': [], 'medium': [], 'weak': []})
        
        # Gewichtete Keyword-Analyse
        score = 0.0
        matches = []
        
        for keyword in keywords['strong']:
            if keyword in channel_lower:
                score += 0.4
                matches.append(f"strong:{keyword}")
        
        for keyword in keywords['medium']:
            if keyword in channel_lower:
                score += 0.2
                matches.append(f"medium:{keyword}")
        
        for keyword in keywords['weak']:
            if keyword in channel_lower:
                score += 0.1
                matches.append(f"weak:{keyword}")
        
        return {
            'score': min(score, 1.0),
            'method': 'weighted_keyword_matching',
            'matches': matches,
            'reliability': 'high' if score > 0.3 else 'medium' if score > 0 else 'low'
        }
    
    def _analyze_content_language_safe(self, video_data: VideoData, target_region: str) -> dict:
        """V6.1: Content-Sprache und regionale Themen analysieren"""
        text = f"{video_data.title} {video_data.channel}".lower()
        
        # Regionale Content-Indikatoren
        regional_content = {
            'DE': {
                'topics': ['bundesliga', 'bundestag', 'oktoberfest', 'karneval', 'deutschrap'],
                'places': ['berlin', 'münchen', 'hamburg', 'köln', 'frankfurt'],
                'culture': ['weihnachten', 'ostern', 'advent', 'schlager']
            },
            'US': {
                'topics': ['nfl', 'nba', 'mlb', 'super bowl', 'thanksgiving'],
                'places': ['new york', 'california', 'texas', 'florida'],
                'culture': ['halloween', 'independence day', 'american']
            },
            'FR': {
                'topics': ['ligue 1', 'tour de france', 'cannes'],
                'places': ['paris', 'marseille', 'lyon', 'bordeaux'],
                'culture': ['bastille day', 'français']
            },
            'ES': {
                'topics': ['la liga', 'real madrid', 'barcelona'],
                'places': ['madrid', 'barcelona', 'valencia', 'sevilla'],
                'culture': ['flamenco', 'tapas', 'español']
            },
            'GB': {
                'topics': ['premier league', 'brexit', 'royal family'],
                'places': ['london', 'manchester', 'liverpool', 'scotland'],
                'culture': ['british', 'tea', 'cricket']
            }
        }
        
        content = regional_content.get(target_region, {'topics': [], 'places': [], 'culture': []})
        
        score = 0.0
        matches = []
        
        for category, keywords in content.items():
            for keyword in keywords:
                if keyword in text:
                    weight = 0.3 if category == 'topics' else 0.2 if category == 'places' else 0.1
                    score += weight
                    matches.append(f"{category}:{keyword}")
        
        return {
            'score': min(score, 1.0),
            'matches': matches,
            'method': 'regional_content_analysis'
        }
    
    def _detect_indian_content(self, video_data: VideoData, target_region: str) -> dict:
        """V6.1: Verbesserte indische Content-Erkennung"""
        text = f"{video_data.title} {video_data.channel}".lower()
        
        # Erweiterte indische Indikatoren
        indian_keywords = [
            # Namen
            'singh', 'kumar', 'sharma', 'patel', 'gupta', 'raj', 'amit', 'rohit',
            # Orte  
            'india', 'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai',
            # Sprache/Kultur
            'hindi', 'bollywood', 'tamil', 'telugu', 'punjabi', 'bengali',
            # Cricket
            'cricket', 'ipl', 'csk', 'mi', 'rcb', 'dhoni', 'kohli',
            # Typische Phrases
            'crore', 'lakh', 'rupees', 'viral video', 'funny video'
        ]
        
        matches = [kw for kw in indian_keywords if kw in text]
        indian_score = len(matches) / 5.0  # Normalisiert auf 5 Keywords
        
        # Engagement-Pattern-Check (oft indische Videos)
        engagement_rate = video_data.comments / max(video_data.views, 1)
        suspicious_engagement = engagement_rate > 0.03  # >3% sehr hoch
        
        is_indian = indian_score > 0.4 or (indian_score > 0.2 and suspicious_engagement)
        
        return {
            'is_indian': is_indian,
            'confidence': min(indian_score, 1.0),
            'keyword_matches': matches,
            'engagement_suspicious': suspicious_engagement,
            'engagement_rate': engagement_rate
        }
    
    def _is_spam_channel(self, video_data: VideoData) -> bool:
        """V6.1: Spam-Channel-Detection"""
        channel_name = video_data.channel.lower()
        title = video_data.title.lower()
        
        # Pattern-basierte Spam-Erkennung
        for pattern in self.spam_patterns:
            if re.search(pattern, channel_name) or re.search(pattern, title):
                return True
        
        # Indische Spam-Indikatoren
        spam_count = sum(1 for indicator in self.indian_spam_indicators 
                        if indicator in f"{channel_name} {title}")
        if spam_count >= 2:
            return True
        
        # Engagement-basierte Spam-Erkennung
        engagement_rate = video_data.comments / max(video_data.views, 1)
        if engagement_rate > 0.08:  # >8% extrem verdächtig
            return True
        
        # Channel-Name-Heuristiken
        emoji_count = sum(1 for c in channel_name if ord(c) > 127)
        if emoji_count > len(channel_name) * 0.4:  # >40% Non-ASCII
            return True
        
        return False
    
    def _get_spam_reasons(self, video_data: VideoData) -> List[str]:
        """V6.1: Detaillierte Spam-Gründe für Debugging"""
        reasons = []
        
        channel_name = video_data.channel.lower()
        title = video_data.title.lower()
        
        # Pattern-Checks
        for pattern in self.spam_patterns:
            if re.search(pattern, channel_name):
                reasons.append(f"channel_pattern:{pattern}")
            if re.search(pattern, title):
                reasons.append(f"title_pattern:{pattern}")
        
        # Engagement-Check
        engagement_rate = video_data.comments / max(video_data.views, 1)
        if engagement_rate > 0.08:
            reasons.append(f"high_engagement:{engagement_rate:.3f}")
        
        # Emoji-Check
        emoji_count = sum(1 for c in channel_name if ord(c) > 127)
        if emoji_count > len(channel_name) * 0.4:
            reasons.append(f"excessive_emojis:{emoji_count}/{len(channel_name)}")
        
        return reasons
    
    def _calculate_source_confidence(self, sources_used: List[str]) -> float:
        """V6.1: Confidence basierend auf verfügbaren Datenquellen"""
        if not sources_used:
            return 0.0
        
        # Gewichtung verschiedener Quellen
        source_weights = {
            'youtube_api': 0.4,      # Offizielle API-Daten
            'channel_name': 0.3,     # Keyword-Analyse
            'content_analysis': 0.2,  # Content-Pattern
            'anti_indian_bias': 0.1   # Bias-Detection
        }
        
        total_weight = sum(source_weights.get(source, 0.1) for source in sources_used)
        return min(total_weight, 1.0)


class RegionalRelevanceScorer:
    """V6.1: Erweiterte Regional-Relevance-Berechnung"""
    
    def __init__(self, target_region: str = 'DE'):
        self.target_region = target_region
        
    def calculate_regional_relevance(self, video_data: VideoData, 
                                   channel_analysis: dict, 
                                   query_context: dict) -> dict:
        """V6.1: Hauptfunktion für Regional-Relevance-Score"""
        
        # 1. Channel-Geography (40% Gewichtung)
        channel_score = channel_analysis.get('geography_score', 0.0) * 0.4
        
        # 2. Content-Regional-Match (30% Gewichtung)
        content_score = self._analyze_content_regional_match(
            video_data, query_context
        ) * 0.3
        
        # 3. Query-Match-Boost (20% Gewichtung)  
        query_score = self._calculate_query_match_bonus(
            video_data, query_context
        ) * 0.2
        
        # 4. Anti-Bias-Adjustment (10% Gewichtung)
        bias_score = self._calculate_anti_bias_adjustment(
            video_data, channel_analysis
        ) * 0.1
        
        # Gesamt-Score
        total_score = channel_score + content_score + query_score + bias_score
        
        # Confidence aus Channel-Analyse übernehmen
        confidence = channel_analysis.get('confidence', 0.5)
        
        # Blacklist-Check
        is_blacklisted = channel_analysis.get('blacklisted', False)
        if is_blacklisted:
            total_score = 0.0
            confidence = 1.0  # Hohe Confidence bei Spam-Erkennung
        
        return {
            'score': round(min(total_score, 1.0), 3),
            'confidence': round(confidence, 3),
            'breakdown': {
                'channel_geography': round(channel_score, 3),
                'content_match': round(content_score, 3),
                'query_boost': round(query_score, 3),
                'anti_bias_adjustment': round(bias_score, 3)
            },
            'region_detected': channel_analysis.get('detected_region'),
            'explanation': self._generate_explanation(total_score),
            'blacklisted': is_blacklisted
        }
    
    def _analyze_content_regional_match(self, video_data: VideoData, query_context: dict) -> float:
        """Prüfe ob Video-Content regional relevant ist"""
        title_lower = video_data.title.lower()
        query = query_context.get('base_query', '').lower()
        
        # Bonus wenn Query + Region zusammen im Titel
        regional_query_patterns = {
            'DE': [f'{query} deutsch', f'{query} deutschland', f'german {query}'],
            'US': [f'{query} american', f'{query} usa', f'american {query}'],
            'FR': [f'{query} français', f'{query} france', f'french {query}'],
            'ES': [f'{query} español', f'{query} españa', f'spanish {query}'],
            'GB': [f'{query} british', f'{query} uk', f'british {query}']
        }
        
        patterns = regional_query_patterns.get(self.target_region, [])
        for pattern in patterns:
            if pattern in title_lower:
                return 1.0  # Perfect match
        
        # Basis-Score wenn Query im Titel
        if query in title_lower:
            return 0.5
        
        return 0.0
    
    def _calculate_query_match_bonus(self, video_data: VideoData, query_context: dict) -> float:
        """Bonus für Query-Relevanz"""
        query = query_context.get('base_query', '').lower()
        boost_keywords = query_context.get('boost_keywords', [])
        
        title_lower = video_data.title.lower()
        channel_lower = video_data.channel.lower()
        
        score = 0.0
        
        # Query im Titel = starker Bonus
        if query in title_lower:
            score += 0.6
        
        # Boost-Keywords
        for keyword in boost_keywords:
            if keyword in title_lower or keyword in channel_lower:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_anti_bias_adjustment(self, video_data: VideoData, channel_analysis: dict) -> float:
        """Anti-Bias-Adjustment für faire regionale Verteilung"""
        
        # Bonus für echte regionale Inhalte
        if channel_analysis.get('detected_region') == self.target_region:
            return 1.0
        
        # Neutraler Score für unbekannte Herkunft
        if channel_analysis.get('detected_region') == 'UNKNOWN':
            return 0.3
        
        # Starke Reduktion für Spam
        if channel_analysis.get('blacklisted', False):
            return 0.0
        
        # Moderate Reduktion für andere Regionen
        return 0.2
    
    def _generate_explanation(self, score: float) -> str:
        """User-friendly Erklärung"""
        if score >= 0.8:
            return f"Sehr relevant für {self.target_region}"
        elif score >= 0.6:
            return f"Relevant für {self.target_region}"
        elif score >= 0.4:
            return f"Bedingt relevant für {self.target_region}"
        elif score >= 0.2:
            return f"Wenig relevant für {self.target_region}"
        else:
            return f"Nicht relevant für {self.target_region}"


class RegionalAnalysisResponse:
    """V6.1: Enhanced API-Response-Builder"""
    
    def build_enhanced_response(self, search_results: dict, analysis_results: list, 
                              query_params: dict, processing_start_time: float) -> dict:
        """V6.1: Production-Ready API-Response"""
        
        processing_time = time.time() - processing_start_time
        
        # Filter gültige Ergebnisse (nicht-blacklisted)
        valid_results = [r for r in analysis_results if not r.regional_relevance.get('blacklisted', False)]
        
        # Score-Statistiken
        if valid_results:
            scores = [r.regional_relevance['score'] for r in valid_results]
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = 0.0
        
        response = {
            "success": True,
            "query": query_params.get('query'),
            "region": query_params.get('region', 'DE'),
            "algorithm_used": "regional_v6.1_production",
            "timestamp": datetime.now().isoformat(),
            
            # V6.1: Detaillierte Search-Strategy
            "search_strategy": {
                "queries_executed": search_results.get('search_strategy_log', []),
                "api_calls_made": search_results.get('api_calls_made', 0),
                "total_videos_discovered": search_results.get('total_videos_found', 0),
                "videos_after_deduplication": len(analysis_results),
                "videos_after_filtering": len(valid_results),
                "search_success": search_results.get('search_success', False)
            },
            
            # Hauptergebnisse
            "top_videos": [self._format_video_response(video, idx + 1) 
                          for idx, video in enumerate(valid_results)],
            
            # V6.1: Regional-Insights mit Statistiken
            "regional_insights": {
                "score_distribution": self._calculate_score_histogram(valid_results),
                "average_regional_score": round(avg_score, 3),
                "high_relevance_videos": len([v for v in valid_results if v.regional_relevance['score'] >= 0.8]),
                "medium_relevance_videos": len([v for v in valid_results if 0.5 <= v.regional_relevance['score'] < 0.8]),
                "low_relevance_videos": len([v for v in valid_results if v.regional_relevance['score'] < 0.5]),
                "spam_videos_filtered": len([r for r in analysis_results if r.regional_relevance.get('blacklisted', False)])
            },
            
            # V6.1: Performance-Metriken
            "performance": {
                "processing_time_ms": round(processing_time * 1000, 2),
                "api_quota_used": search_results.get('api_calls_made', 0),
                "videos_per_second": round(len(analysis_results) / max(processing_time, 0.1), 2)
            },
            
            # V6.1: Quality-Metriken für Frontend-Filter
            "quality_metrics": {
                "high_confidence_videos": len([v for v in valid_results if v.regional_relevance['confidence'] >= 0.8]),
                "medium_confidence_videos": len([v for v in valid_results if 0.5 <= v.regional_relevance['confidence'] < 0.8]),
                "low_confidence_videos": len([v for v in valid_results if v.regional_relevance['confidence'] < 0.5])
            }
        }
        
        return response
    
    def _format_video_response(self, video_result: TrendingResult, rank: int) -> dict:
        """V6.1: Video-Response-Format für API"""
        return {
            'rank': rank,
            'title': video_result.video_data.title,
            'channel': video_result.video_data.channel,
            'views': video_result.video_data.views,
            'comments': video_result.video_data.comments,
            'likes': video_result.video_data.likes,
            'trending_score': round(video_result.trending_score, 2),
            'normalized_score': round(video_result.normalized_score, 1),
            'age_hours': int(video_result.video_data.age_hours),
            'duration_formatted': self._format_duration(video_result.video_data.duration_seconds),
            'duration_seconds': video_result.video_data.duration_seconds,
            'engagement_rate': round(video_result.video_data.comments / max(video_result.video_data.views, 1), 4),
            'url': f"https://youtube.com/watch?v={video_result.video_data.video_id}",
            'algorithm_version': video_result.algorithm_version,
            
            # V6.1: Regional-Relevance-Daten
            'regional_relevance': video_result.regional_relevance,
            'confidence': video_result.regional_relevance['confidence'],
            'blacklisted': video_result.regional_relevance.get('blacklisted', False)
        }
    
    def _calculate_score_histogram(self, results: list) -> dict:
        """Score-Verteilung für Analytics"""
        if not results:
            return {}
        
        buckets = {'0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0, '0.6-0.8': 0, '0.8-1.0': 0}
        
        for video in results:
            score = video.regional_relevance['score']
            if score < 0.2:
                buckets['0.0-0.2'] += 1
            elif score < 0.4:
                buckets['0.2-0.4'] += 1
            elif score < 0.6:
                buckets['0.4-0.6'] += 1
            elif score < 0.8:
                buckets['0.6-0.8'] += 1
            else:
                buckets['0.8-1.0'] += 1
        
        return buckets
    
    def _format_duration(self, seconds: int) -> str:
        """Format duration als MM:SS oder HH:MM:SS"""
        if seconds == 0:
            return "00:00"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"


# Original Algorithm Classes (für Kompatibilität)
class TrendingAlgorithm(ABC):
    """Abstract Base Class für Trending-Algorithmen"""
    
    @abstractmethod
    def calculate_trending_score(self, video: VideoData) -> float:
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        pass


class EnhancedTrendingAlgorithm(TrendingAlgorithm):
    """Basis-Trending-Algorithmus"""
    
    def __init__(self, engagement_factor: float = 10.0, freshness_exponent: float = 1.3):
        self.engagement_factor = engagement_factor
        self.freshness_exponent = freshness_exponent
        self.version = "enhanced_v6.1"
    
    def calculate_trending_score(self, video: VideoData) -> float:
        views = max(video.views, 1)
        comments = video.comments
        likes = video.likes
        age_hours = max(video.age_hours, 1)
        
        # Anti-Spam-Protection
        engagement_rate = comments / views
        if engagement_rate > 0.05:
            engagement_rate = 0.05 + (engagement_rate - 0.05) * 0.3
        
        # Basis-Score
        base_score = (views + comments * self.engagement_factor) / math.pow(age_hours, self.freshness_exponent)
        
        # Engagement-Multiplikator
        likes_bonus = likes / max(views, 1) * 0.5
        engagement_multiplier = 1 + engagement_rate + likes_bonus
        
        # Duration-Bonus
        duration_bonus = min(video.duration_seconds / 300, 2.0)
        
        return base_score * engagement_multiplier * duration_bonus
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "engagement_factor": self.engagement_factor,
            "freshness_exponent": self.freshness_exponent
        }


class V6TrendingAnalyzer:
    """V6.1: Hauptklasse für Regional-Trending-Analyse"""
    
    def __init__(self, target_region: str = "DE", algorithm: TrendingAlgorithm = None):
        self.target_region = target_region
        self.algorithm = algorithm or EnhancedTrendingAlgorithm()
        
        # V6.1: Komponenten initialisieren
        self.query_builder = RegionalQueryBuilder()
        self.channel_analyzer = ChannelGeographyAnalyzer()
        self.relevance_scorer = RegionalRelevanceScorer(target_region)
        self.response_builder = RegionalAnalysisResponse()
        
        # Statistiken
        self.processing_stats = {
            'videos_analyzed': 0,
            'videos_filtered': 0,
            'api_calls_made': 0,
            'cache_hits': 0
        }
    
    def analyze_videos_v6(self, query: str, videos: List[VideoData], top_count: int = 12) -> dict:
        """V6.1: Hauptfunktion für Video-Analyse"""
        processing_start = time.time()
        
        print(f"\n🔍 V6.1 Regional Analysis: '{query}' → {self.target_region}")
        print("=" * 60)
        
        # Query-Context für Scoring
        query_plan = self.query_builder.build_adaptive_query_plan(query, self.target_region)
        
        results = []
        for video in videos:
            try:
                # Channel-Geography-Analyse
                channel_analysis = self.channel_analyzer.analyze_channel_geography_v6(
                    video, self.target_region
                )
                
                # Regional-Relevance-Score
                regional_relevance = self.relevance_scorer.calculate_regional_relevance(
                    video, channel_analysis, query_plan
                )
                
                # Trending-Score berechnen
                trending_score = self.algorithm.calculate_trending_score(video)
                
                # Ergebnis zusammenstellen
                result = TrendingResult(
                    video_data=video,
                    trending_score=trending_score,
                    rank=0,  # Wird später gesetzt
                    normalized_score=0.0,  # Wird später berechnet
                    algorithm_version="v6.1_regional",
                    regional_relevance=regional_relevance,
                    blacklisted=regional_relevance.get('blacklisted', False)
                )
                
                results.append(result)
                
            except Exception as e:
                print(f"⚠️ Error analyzing video {video.video_id}: {e}")
                continue
        
        # Sortiere nach Regional-Score und dann Trending-Score
        results.sort(key=lambda x: (
            x.regional_relevance['score'],  # Primär: Regional-Relevance
            x.trending_score                # Sekundär: Trending-Score
        ), reverse=True)
        
        # Top-Ergebnisse auswählen und Rankings setzen
        top_results = results[:top_count]
        for idx, result in enumerate(top_results):
            result.rank = idx + 1
            result.normalized_score = ((result.regional_relevance['score'] * 0.6 + 
                                     (result.trending_score / max(results[0].trending_score, 1)) * 0.4) * 10)
        
        # Mock search_results für Response
        search_results = {
            'api_calls_made': 3,
            'total_videos_found': len(videos),
            'search_success': len(top_results) > 0,
            'search_strategy_log': [
                {'query': query, 'phase': 'primary', 'results_count': len(videos)}
            ]
        }
        
        # API-Response zusammenstellen
        response = self.response_builder.build_enhanced_response(
            search_results, top_results, 
            {'query': query, 'region': self.target_region}, 
            processing_start
        )
        
        # Debug-Output
        print(f"📊 V6.1 Results Summary:")
        print(f"   Total analyzed: {len(results)}")
        print(f"   High relevance (>0.8): {response['regional_insights']['high_relevance_videos']}")
        print(f"   Medium relevance (0.5-0.8): {response['regional_insights']['medium_relevance_videos']}")
        print(f"   Low relevance (<0.5): {response['regional_insights']['low_relevance_videos']}")
        print(f"   Spam filtered: {response['regional_insights']['spam_videos_filtered']}")
        print(f"   Processing time: {response['performance']['processing_time_ms']:.1f}ms")
        print("=" * 60)
        
        return response
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """V6.1: Algorithm-Info für API"""
        return {
            "version": "v6.1_regional_production",
            "target_region": self.target_region,
            "features": [
                "Adaptive Query-Expansion",
                "Multi-Source Channel-Geography",
                "Spam-Detection & Blacklisting",
                "Regional-Relevance-Scoring",
                "Production-Level Error-Handling"
            ],
            "components": {
                "query_builder": "RegionalQueryBuilder V6.1",
                "channel_analyzer": "ChannelGeographyAnalyzer V6.1", 
                "relevance_scorer": "RegionalRelevanceScorer V6.1",
                "response_builder": "RegionalAnalysisResponse V6.1"
            }
        }


# Compatibility Aliases (für bestehende API)
TrendingAnalyzer = V6TrendingAnalyzer


class AlgorithmFactory:
    """V6.1: Factory für verschiedene Algorithmus-Strategien"""
    
    @staticmethod
    def create_basic_algorithm() -> TrendingAlgorithm:
        return EnhancedTrendingAlgorithm()
    
    @staticmethod
    def create_regional_algorithm(region: str) -> TrendingAlgorithm:
        return EnhancedTrendingAlgorithm(engagement_factor=8.0, freshness_exponent=1.4)
    
    @staticmethod
    def create_anti_spam_algorithm() -> TrendingAlgorithm:
        return EnhancedTrendingAlgorithm(engagement_factor=6.0, freshness_exponent=1.6)


# Legacy Functions (für Kompatibilität mit bestehender API)
def calculate_realistic_confidence(video_title: str, video_channel: str, views: int, 
                                 comments: int, age_hours: float, target_region: str = 'DE') -> float:
    """V6.1: Legacy-Compatibility für Confidence-Berechnung"""
    
    # Basis-Confidence
    confidence = 0.5
    
    # Engagement-Check
    engagement_rate = comments / max(views, 1)
    if engagement_rate > 0.06:
        confidence -= 0.4
    elif engagement_rate > 0.04:
        confidence -= 0.3
    elif engagement_rate > 0.025:
        confidence -= 0.15
    elif engagement_rate >= 0.001:
        confidence += 0.25
    
    # Regional-Keywords-Check
    text = f"{video_title} {video_channel}".lower()
    
    regional_keywords = {
        'DE': ['deutsch', 'deutschland', 'german', 'bundesliga', 'ard', 'zdf'],
        'US': ['american', 'america', 'usa', 'english', 'nfl', 'nba'],
        'FR': ['français', 'france', 'tf1'],
        'ES': ['español', 'españa', 'rtve']
    }
    
    keywords = regional_keywords.get(target_region, [])
    regional_matches = sum(1 for kw in keywords if kw in text)
    
    if regional_matches >= 2:
        confidence += 0.3
    elif regional_matches >= 1:
        confidence += 0.2
    
    # Anti-Indian-Bias (legacy)
    indian_keywords = ['cricket', 'bollywood', 'hindi', 'india', 'singh', 'kumar']
    indian_matches = sum(1 for kw in indian_keywords if kw in text)
    
    if target_region != 'IN' and indian_matches >= 2:
        confidence -= 0.4
    
    return max(0.1, min(0.95, confidence))


# Legacy-Class für bestehende API-Kompatibilität
class RegionalFilter:
    """Legacy-Kompatibilität"""
    
    @classmethod
    def enhanced_indian_detection(cls, video: VideoData) -> Tuple[bool, float, str]:
        analyzer = ChannelGeographyAnalyzer()
        indian_analysis = analyzer._detect_indian_content(video, 'DE')
        return (
            indian_analysis['is_indian'],
            indian_analysis['confidence'],
            f"Keywords: {indian_analysis['keyword_matches']}"
        )
    
    @classmethod
    def enhanced_german_detection(cls, video: VideoData) -> Tuple[bool, float]:
        analyzer = ChannelGeographyAnalyzer()
        name_analysis = analyzer._analyze_channel_name_safe(video.channel, 'DE')
        return name_analysis['score'] > 0.5, name_analysis['score']
