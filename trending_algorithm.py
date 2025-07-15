# trending_algorithm.py - KOMPLETTE DATEI mit V5.0 Enhanced Regional Filter
"""
Modularer YouTube Trending Algorithmus mit V5.0 Enhanced Regional Filter
Löst das indische Video-Dominanz Problem direkt im Algorithmus-Layer
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import math
import re


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
    algorithm_version: str = "v1.0"
    filter_applied: Optional[str] = None
    is_indian_content: bool = False
    is_regional_content: bool = False


class RegionalFilter:
    """V5.0 Enhanced Regional Filter - Anti-Indian-Bias Solution"""
    
    # V5.0 ERWEITERTE KEYWORD-LISTEN
    INDIAN_INDICATORS = [
        # Namen (häufigste)
        'singh', 'kumar', 'sharma', 'patel', 'raj', 'amit', 'rohit', 'deepak',
        'gupta', 'agarwal', 'jain', 'yadav', 'suresh', 'ramesh', 'vikash',
        'santosh', 'pradeep', 'ajay', 'sanjay', 'manoj', 'ankit', 'ravi',
        
        # Orte
        'mumbai', 'delhi', 'bangalore', 'hyderabad', 'chennai', 'kolkata',
        'pune', 'ahmedabad', 'jaipur', 'lucknow', 'kanpur', 'nagpur', 'indore',
        
        # Sprachen/Kultur
        'bollywood', 'hindi', 'tamil', 'telugu', 'malayalam', 'bengali', 
        'gujarati', 'marathi', 'punjabi', 'bhojpuri', 'desi', 'hindustani',
        'urdu', 'sanskrit',
        
        # Cricket (sehr spezifisch indisch)
        'cricket', 'ipl', 'csk', 'mi', 'rcb', 'kkr', 'srh', 'dc', 'pbks', 'rr',
        'dhoni', 'kohli', 'rohit sharma', 'virat', 'wicket', 'sixer', 'boundary',
        'test match', 'odi', 't20', 'bcci',
        
        # Typische Hindi/Indische Phrases
        'subscribe karo', 'like kijiye', 'share karo', 'comment karo',
        'bell icon dabaye', 'notification on karo', 'channel ko subscribe',
        'video accha laga', 'dekhen jarur',
        
        # Content-Typen
        'viral video', 'funny video', 'bhajan', 'kirtan', 'mantra', 'aarti',
        'temple', 'gurdwara', 'festival', 'holi', 'diwali', 'navratri',
        'ganesh', 'durga', 'ram', 'krishna', 'hanuman',
        
        # Film/Entertainment
        'tollywood', 'kollywood', 'mollywood', 'sandalwood', 'bhojpuri cinema',
        'item song', 'masala', 'tadka',
        
        # Sonstige
        'rupees', 'crore', 'lakh', 'paisa', 'indian', 'india', 'bharat', 'hindustan'
    ]
    
    GERMAN_INDICATORS = [
        # Orte
        'deutschland', 'german', 'deutsch', 'berlin', 'münchen', 'hamburg', 
        'köln', 'frankfurt', 'stuttgart', 'düsseldorf', 'dortmund', 'essen',
        'leipzig', 'bremen', 'dresden', 'hannover', 'nürnberg', 'duisburg',
        'österreich', 'schweiz', 'wien', 'zürich', 'basel', 'salzburg',
        'innsbruck', 'graz', 'linz', 'bern', 'genf',
        
        # Sport
        'bundesliga', 'bayern', 'dortmund', 'schalke', 'leipzig', 'leverkusen',
        'dfb', 'nationalmannschaft', 'em', 'wm', 'fußball', 'werder', 'hsv',
        'eintracht', 'gladbach', 'hoffenheim', 'mainz', 'augsburg',
        
        # Medien
        'ard', 'zdf', 'rtl', 'sat1', 'pro7', 'vox', 'sport1', 'dazn',
        'bild', 'spiegel', 'focus', 'stern', 'welt', 'zeit', 'sueddeutsche',
        
        # Kultur/Events
        'oktoberfest', 'karneval', 'weihnachten', 'ostern', 'advent',
        'deutschrap', 'schlager', 'volksfest', 'kirmes', 'fasching',
        
        # Politik/Personen
        'bundestag', 'kanzler', 'merkel', 'scholz', 'afd', 'cdu', 'spd',
        'grüne', 'fdp', 'linke', 'bayern', 'nrw', 'baden-württemberg'
    ]
    
    @classmethod
    def enhanced_indian_detection(cls, video: VideoData) -> Tuple[bool, float, str]:
        """
        V5.0 - Verstärkte Erkennung indischer Videos
        Returns: (is_indian, confidence_score, reason)
        """
        text = f"{video.title} {video.channel}".lower()
        
        # 1. KEYWORD-SCORE (0-1)
        indian_matches = [kw for kw in cls.INDIAN_INDICATORS if kw in text]
        keyword_score = min(len(indian_matches) / 2.5, 1.0)  # Normalisiert auf 2.5 Keywords
        
        # 2. ENGAGEMENT-PATTERN-SCORE (typisch für indische Videos)
        engagement_rate = video.comments / max(video.views, 1)
        engagement_score = 0.0
        
        if engagement_rate > 0.06:     # >6% = extrem verdächtig
            engagement_score = 1.0
        elif engagement_rate > 0.04:   # >4% = sehr verdächtig
            engagement_score = 0.8
        elif engagement_rate > 0.025:  # >2.5% = verdächtig
            engagement_score = 0.5
        elif engagement_rate > 0.015:  # >1.5% = etwas verdächtig
            engagement_score = 0.2
            
        # 3. NAME-PATTERN-SCORE (typische indische Namen)
        name_patterns = [
            r'\b\w*(singh|kumar|sharma|patel|gupta|agarwal|jain|yadav)\b',
            r'\b(raj|dev|amit|rohit|suresh|deepak|vikash|santosh|pradeep)\s*\w*\b',
            r'\b\w*\s*(official|entertainment|music|films|bhojpuri|punjabi)\b'
        ]
        
        name_score = 0.0
        name_matches = []
        for pattern in name_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                name_score += 0.35
                name_matches.append(pattern.split('|')[0])  # Erstes Keyword für Debug
        name_score = min(name_score, 1.0)
        
        # 4. TITLE-PATTERN-SCORE (typische Titel-Patterns)
        suspicious_patterns = [
            (r'[😭💔😢😍❤️🙏]{2,}', 'MultiEmoji'),
            (r'\|\|.*\|\|', 'DoublePipe'),
            (r'viral\s*(video|song|dance)', 'ViralContent'),
            (r'(subscribe|like)\s*(karo|kijiye)', 'HindiCTA'),
            (r'(funny|comedy|entertainment)\s*(video|clip)', 'EntertainmentSpam'),
            (r'(bhojpuri|punjabi|tamil|hindi)\s*(song|video|music)', 'RegionalContent'),
            (r'\d+\s*(crore|lakh)\s*(views|subscribers)', 'IndianNumbers')
        ]
        
        pattern_score = 0.0
        pattern_matches = []
        for pattern, name in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_score += 0.15
                pattern_matches.append(name)
        pattern_score = min(pattern_score, 1.0)
        
        # 5. VIEWS-TO-AGE SUSPICIOUS PATTERN
        views_per_hour = video.views / max(video.age_hours, 1)
        suspicious_growth_score = 0.0
        
        # Sehr schnelles Wachstum mit hohem Engagement = oft indische Videos
        if views_per_hour > 50000 and engagement_rate > 0.03:
            suspicious_growth_score = 0.3
        elif views_per_hour > 20000 and engagement_rate > 0.02:
            suspicious_growth_score = 0.2
        
        # 6. GESAMTSCORE BERECHNEN
        total_score = (
            keyword_score * 0.35 +        # 35% Keywords (wichtigster Faktor)
            engagement_score * 0.25 +     # 25% Engagement-Pattern
            name_score * 0.20 +           # 20% Name-Pattern
            pattern_score * 0.15 +        # 15% Title-Pattern
            suspicious_growth_score * 0.05 # 5% Growth-Pattern
        )
        
        # FINAL DECISION mit adaptiver Schwelle
        base_threshold = 0.35
        
        # Niedrigere Schwelle für sehr verdächtige Engagement-Patterns
        if engagement_rate > 0.05:
            threshold = 0.25  # Sehr niedrig bei extremem Engagement
        elif engagement_rate > 0.03:
            threshold = 0.30  # Niedrig bei hohem Engagement
        else:
            threshold = base_threshold
            
        is_indian = total_score >= threshold
        
        # REASON STRING für Debugging
        reasons = []
        if indian_matches: 
            reasons.append(f"Keywords({','.join(indian_matches[:3])})")
        if engagement_score > 0.4: 
            reasons.append(f"HighEng({engagement_rate:.1%})")
        if name_matches: 
            reasons.append(f"Names({','.join(name_matches[:2])})")
        if pattern_matches: 
            reasons.append(f"Patterns({','.join(pattern_matches[:2])})")
        if suspicious_growth_score > 0.1:
            reasons.append(f"SuspiciousGrowth({views_per_hour:.0f}/h)")
        
        reason = " + ".join(reasons) if reasons else "Clean"
        
        return is_indian, total_score, reason
    
    @classmethod
    def enhanced_german_detection(cls, video: VideoData) -> Tuple[bool, float]:
        """
        V5.0 - Verstärkte Erkennung deutscher Inhalte
        Returns: (is_german, confidence_score)
        """
        text = f"{video.title} {video.channel}".lower()
        
        # Keyword-Matching
        german_matches = [kw for kw in cls.GERMAN_INDICATORS if kw in text]
        german_score = min(len(german_matches) / 1.5, 1.0)  # Normalisiert auf 1.5 Keywords
        
        # Bonus für eindeutige deutsche Indikatoren
        strong_german_indicators = [
            'deutschland', 'bundesliga', 'ard', 'zdf', 'bayern münchen',
            'dortmund', 'bundestag', 'oktoberfest', 'deutschrap'
        ]
        
        strong_matches = sum(1 for indicator in strong_german_indicators if indicator in text)
        if strong_matches > 0:
            german_score += 0.3  # Starker Bonus
            
        # Channel-Name-Bonus
        german_channel_indicators = ['deutschland', 'german', 'deutsch', 'tv', 'ard', 'zdf']
        if any(indicator in video.channel.lower() for indicator in german_channel_indicators):
            german_score += 0.2
            
        is_german = german_score >= 0.4
        return is_german, min(german_score, 1.0)
    
    @classmethod
    def detect_content_language(cls, video: VideoData) -> Optional[str]:
        """Erkenne die wahrscheinliche Sprache des Videos (erweitert)"""
        text = f"{video.title} {video.channel}".lower()
        
        # Erweiterte Sprach-Pattern
        language_patterns = {
            'hindi': cls.INDIAN_INDICATORS,
            'german': cls.GERMAN_INDICATORS,
            'spanish': ['español', 'españa', 'mexico', 'madrid', 'barcelona'],
            'french': ['français', 'france', 'paris', 'québec'],
            'english': ['english', 'america', 'british', 'london', 'new york']
        }
        
        scores = {}
        for language, patterns in language_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                scores[language] = score
        
        if not scores:
            return None
            
        return max(scores, key=scores.get)


class TrendingAlgorithm(ABC):
    """Abstract Base Class für Trending-Algorithmen"""
    
    @abstractmethod
    def calculate_trending_score(self, video: VideoData) -> float:
        """Berechne Trending-Score für ein Video"""
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Informationen über den Algorithmus"""
        pass


class EnhancedTrendingAlgorithm(TrendingAlgorithm):
    """Verbesserter Trending-Algorithmus mit regionaler Optimierung"""
    
    def __init__(self, 
                 engagement_factor: float = 10.0,
                 freshness_exponent: float = 1.3,
                 regional_boost: float = 1.5,
                 anti_spam_threshold: float = 0.05):
        self.engagement_factor = engagement_factor
        self.freshness_exponent = freshness_exponent
        self.regional_boost = regional_boost
        self.anti_spam_threshold = anti_spam_threshold
        self.version = "enhanced_v2.0"
    
    def calculate_trending_score(self, video: VideoData) -> float:
        """Erweiterte Trending-Score-Berechnung"""
        
        # Basis-Metriken
        views = max(video.views, 1)
        comments = video.comments
        likes = video.likes
        age_hours = max(video.age_hours, 1)
        
        # Engagement-Rate mit Anti-Spam-Protection
        engagement_rate = comments / views
        if engagement_rate > self.anti_spam_threshold:
            # Reduziere übermäßiges Engagement (oft Spam/Bots)
            engagement_rate = self.anti_spam_threshold + (engagement_rate - self.anti_spam_threshold) * 0.3
        
        # Basis-Score: Views + Gewichtete Comments / Alter
        base_score = (views + comments * self.engagement_factor) / math.pow(age_hours, self.freshness_exponent)
        
        # Likes-Bonus (positive Engagement)
        likes_bonus = likes / max(views, 1) * 0.5
        
        # Engagement-Multiplikator
        engagement_multiplier = 1 + engagement_rate + likes_bonus
        
        # Duration-Bonus (längere Videos = höhere Retention)
        duration_bonus = min(video.duration_seconds / 300, 2.0)  # Max 2x für 5+ Minuten
        
        # Finaler Score
        trending_score = base_score * engagement_multiplier * duration_bonus
        
        return trending_score
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "engagement_factor": self.engagement_factor,
            "freshness_exponent": self.freshness_exponent,
            "regional_boost": self.regional_boost,
            "anti_spam_threshold": self.anti_spam_threshold,
            "features": [
                "Anti-Spam-Protection",
                "Duration-Bonus",
                "Likes-Integration",
                "Regional-Boost"
            ]
        }


class RegionalOptimizedAlgorithm(EnhancedTrendingAlgorithm):
    """V5.0 Regional optimierter Algorithmus mit Enhanced Anti-Bias Filter"""
    
    def __init__(self, target_region: str = "DE", **kwargs):
        super().__init__(**kwargs)
        self.target_region = target_region
        self.version = "regional_v5.0_enhanced"
        self.indian_videos_processed = 0
        self.german_videos_boosted = 0
        self.max_indian_videos = 1  # V5.0: Maximal 1 indisches Video
    
    def calculate_trending_score(self, video: VideoData) -> float:
        """V5.0 Regional optimierte Score-Berechnung mit Enhanced Filter"""
        
        # Basis-Score berechnen
        base_score = super().calculate_trending_score(video)
        
        # V5.0 ENHANCED REGIONAL ADJUSTMENTS
        if self.target_region and self.target_region != 'IN':
            # Enhanced indische Content-Erkennung
            is_indian, indian_confidence, reason = RegionalFilter.enhanced_indian_detection(video)
            
            if is_indian:
                # V5.0: Drastische Reduktion für indische Videos
                penalty_factor = 0.02 + (0.08 * (1 - indian_confidence))  # 2-10% vom Original
                base_score *= penalty_factor
                self.indian_videos_processed += 1
                
                print(f"🚫 V5.0 INDIAN PENALTY: {video.title[:50]}...")
                print(f"   Confidence: {indian_confidence:.2f} | Reason: {reason}")
                print(f"   Score: {base_score/penalty_factor:.1f} → {base_score:.1f} (-{(1-penalty_factor)*100:.0f}%)")
        
        # V5.0 Enhanced Sprach-Boost für Zielregion
        detected_language = RegionalFilter.detect_content_language(video)
        if detected_language:
            language_boost = self._get_v5_language_boost(detected_language)
            if language_boost > 1.0:
                original_score = base_score
                base_score *= language_boost
                
                if self.target_region == 'DE' and detected_language == 'german':
                    self.german_videos_boosted += 1
                    print(f"✅ V5.0 GERMAN BOOST: {video.title[:50]}...")
                    print(f"   Score: {original_score:.1f} → {base_score:.1f} (+{(language_boost-1)*100:.0f}%)")
        
        return base_score
    
    def _get_v5_language_boost(self, detected_language: str) -> float:
        """V5.0 Enhanced Sprach-Boost basierend auf Zielregion"""
        boost_map = {
            'DE': {
                'german': 1.4,    # +40% für deutsche Inhalte
                'english': 1.1,   # +10% für englische Inhalte  
                'french': 1.05,   # +5% für französische Inhalte
                'hindi': 0.1      # -90% für Hindi-Inhalte
            },
            'US': {
                'english': 1.3,   # +30% für englische Inhalte
                'spanish': 1.15,  # +15% für spanische Inhalte
                'hindi': 0.2      # -80% für Hindi-Inhalte
            },
            'ES': {
                'spanish': 1.4,   # +40% für spanische Inhalte
                'english': 1.1,   # +10% für englische Inhalte
                'hindi': 0.1      # -90% für Hindi-Inhalte
            },
            'FR': {
                'french': 1.4,    # +40% für französische Inhalte
                'english': 1.1,   # +10% für englische Inhalte
                'hindi': 0.1      # -90% für Hindi-Inhalte
            },
            'GB': {
                'english': 1.3,   # +30% für englische Inhalte
                'hindi': 0.2      # -80% für Hindi-Inhalte
            }
        }
        
        if self.target_region in boost_map:
            return boost_map[self.target_region].get(detected_language, 1.0)
        
        # Fallback: Generelle Reduktion für Hindi
        if detected_language == 'hindi':
            return 0.15  # -85% für Hindi-Inhalte
        
        return 1.0
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        info = super().get_algorithm_info()
        info.update({
            "target_region": self.target_region,
            "v5_enhanced_features": [
                "Enhanced Anti-Indian-Bias (95% reduction)",
                "Advanced Pattern Recognition",
                "Engagement-Pattern-Analysis", 
                "Regional-Content-Boost (+40%)",
                "Multi-Language-Detection",
                "Adaptive Threshold Filtering"
            ],
            "v5_statistics": {
                "indian_videos_processed": self.indian_videos_processed,
                "german_videos_boosted": self.german_videos_boosted,
                "max_indian_videos_allowed": self.max_indian_videos
            }
        })
        return info


class V5TrendingAnalyzer:
    """V5.0 Enhanced Analyzer mit Anti-Bias Filter Integration"""
    
    def __init__(self, algorithm: TrendingAlgorithm, target_region: str = "DE"):
        self.algorithm = algorithm
        self.target_region = target_region
        self.filter_stats = {
            "original_count": 0,
            "indian_videos_found": 0,
            "indian_videos_kept": 0,
            "indian_videos_removed": 0,
            "german_videos_boosted": 0,
            "total_score_modifications": 0
        }
    
    def analyze_videos(self, 
                      videos: List[VideoData], 
                      top_count: int = 12,
                      min_score: float = 0.0) -> Tuple[List[TrendingResult], Dict]:
        """V5.0 Enhanced Analyze mit Pre-Filtering"""
        
        self.filter_stats["original_count"] = len(videos)
        
        # V5.0 PRE-FILTERING: Entferne überschüssige indische Videos
        filtered_videos = self._apply_v5_pre_filter(videos)
        
        results = []
        
        for video in filtered_videos:
            # Berechne Trending-Score (inklusive V5.0 Anpassungen im Algorithmus)
            trending_score = self.algorithm.calculate_trending_score(video)
            
            # Skip Videos unter Mindest-Score
            if trending_score < min_score:
                continue
            
            # Zusätzliche V5.0 Analyse für Result-Metadata
            is_indian, indian_conf, reason = RegionalFilter.enhanced_indian_detection(video)
            is_german, german_conf = RegionalFilter.enhanced_german_detection(video)
            
            filter_applied = []
            if is_indian and self.target_region != 'IN':
                filter_applied.append("V5.0 Indian Penalty")
            if is_german and self.target_region == 'DE':
                filter_applied.append("V5.0 German Boost")
            
            results.append(TrendingResult(
                video_data=video,
                trending_score=trending_score,
                rank=0,  # Wird später gesetzt
                normalized_score=0.0,  # Wird später berechnet
                algorithm_version=self.algorithm.version if hasattr(self.algorithm, 'version') else "unknown",
                filter_applied=", ".join(filter_applied) if filter_applied else None,
                is_indian_content=is_indian,
                is_regional_content=is_german if self.target_region == 'DE' else False
            ))
        
        # Sortiere nach Trending-Score
        results.sort(key=lambda x: x.trending_score, reverse=True)
        
        # Setze Rankings und normalisierte Scores
        top_score = results[0].trending_score if results else 1.0
        
        final_results = []
        for i, result in enumerate(results[:top_count], 1):
            result.rank = i
            result.normalized_score = (result.trending_score / top_score) * 10
            final_results.append(result)
        
        return final_results, self.filter_stats
    
    def _apply_v5_pre_filter(self, videos: List[VideoData]) -> List[VideoData]:
        """V5.0 Pre-Filter: Limitiere indische Videos BEVOR Algorithmus-Anwendung"""
        
        if self.target_region == 'IN':
            return videos  # Kein Filter für Indien
        
        print(f"\n🔍 V5.0 Pre-Filter für Region: {self.target_region}")
        print("=" * 50)
        
        filtered_videos = []
        indian_videos_kept = 0
        max_indian_videos = 1  # V5.0: Nur 1 indisches Video
        
        # Sortiere Videos nach Quality-Score für bessere Auswahl
        video_quality_scores = []
        for video in videos:
            engagement_rate = video.comments / max(video.views, 1)
            quality_score = video.views * (1 + min(engagement_rate, 0.02))  # Cap engagement
            video_quality_scores.append((video, quality_score))
        
        # Sortiere nach Quality (beste zuerst)
        video_quality_scores.sort(key=lambda x: x[1], reverse=True)
        
        for video, quality_score in video_quality_scores:
            is_indian, indian_conf, reason = RegionalFilter.enhanced_indian_detection(video)
            
            self.filter_stats["indian_videos_found"] += is_indian
            
            if is_indian:
                print(f"🚫 INDIAN: {video.title[:45]}... (Conf: {indian_conf:.2f})")
                print(f"   Reason: {reason}")
                
                if indian_videos_kept < max_indian_videos:
                    print(f"   ⚠️  KEPT as #{indian_videos_kept + 1} (will be penalized)")
                    filtered_videos.append(video)
                    indian_videos_kept += 1
                    self.filter_stats["indian_videos_kept"] += 1
                else:
                    print(f"   ❌ REMOVED (limit of {max_indian_videos} reached)")
                    self.filter_stats["indian_videos_removed"] += 1
                    continue
            else:
                # Check für deutsche/regionale Inhalte
                if self.target_region == 'DE':
                    is_german, german_conf = RegionalFilter.enhanced_german_detection(video)
                    if is_german:
                        print(f"✅ GERMAN: {video.title[:45]}... (Conf: {german_conf:.2f})")
                        self.filter_stats["german_videos_boosted"] += 1
                
                filtered_videos.append(video)
        
        print("=" * 50)
        print(f"📊 V5.0 Pre-Filter Result:")
        print(f"   Original: {len(videos)} videos")
        print(f"   Indian found: {self.filter_stats['indian_videos_found']}")
        print(f"   Indian kept: {self.filter_stats['indian_videos_kept']}")
        print(f"   Indian removed: {self.filter_stats['indian_videos_removed']}")
        print(f"   Final: {len(filtered_videos)} videos")
        print("=" * 50)
        
        return filtered_videos
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Enhanced Algorithm Info mit V5.0 Statistiken"""
        base_info = self.algorithm.get_algorithm_info()
        base_info.update({
            "v5_analyzer_stats": self.filter_stats,
            "target_region": self.target_region,
            "v5_enhancements": [
                "Pre-Filtering vor Score-Berechnung",
                "Limitierung indischer Videos (max 1)",
                "Quality-basierte Video-Auswahl",
                "Echtzeit Filter-Statistiken"
            ]
        })
        return base_info


# Alias für Kompatibilität (TrendingAnalyzer → V5TrendingAnalyzer)
TrendingAnalyzer = V5TrendingAnalyzer


# Vordefinierte Algorithmus-Strategien (V5.0 Enhanced)
class AlgorithmFactory:
    """V5.0 Enhanced Factory für verschiedene Algorithmus-Strategien"""
    
    @staticmethod
    def create_basic_algorithm() -> TrendingAlgorithm:
        """Basis-Algorithmus ohne regionale Optimierung"""
        return EnhancedTrendingAlgorithm()
    
    @staticmethod
    def create_regional_algorithm(region: str) -> TrendingAlgorithm:
        """V5.0 Enhanced Regional optimierter Algorithmus"""
        return RegionalOptimizedAlgorithm(target_region=region)
    
    @staticmethod
    def create_anti_spam_algorithm() -> TrendingAlgorithm:
        """V5.0 Enhanced Anti-Spam optimierter Algorithmus"""
        return RegionalOptimizedAlgorithm(
            target_region="GLOBAL",
            engagement_factor=8.0,
            anti_spam_threshold=0.015,  # Noch niedrigere Schwelle
            freshness_exponent=1.5
        )


# V5.0 ENHANCED CONFIDENCE-BERECHNUNG
def calculate_realistic_confidence(video_title, video_channel, views, comments, age_hours, target_region='DE'):
    """
    V5.0 Enhanced Confidence-Berechnung mit verstärktem Anti-Bias
    """
    confidence_score = 0.5  # Start bei 50%
    
    # 1. Enhanced Engagement-Check
    engagement_rate = comments / max(views, 1)
    if engagement_rate > 0.06:     # >6% = extrem verdächtig
        confidence_score -= 0.4
    elif engagement_rate > 0.04:   # >4% = sehr verdächtig
        confidence_score -= 0.3
    elif engagement_rate > 0.025:  # >2.5% = verdächtig
        confidence_score -= 0.15
    elif engagement_rate >= 0.001: # 0.1-2.5% = gesund
        confidence_score += 0.25
    
    # 2. V5.0 Enhanced Indien-Check
    text = f"{video_title} {video_channel}".lower()
    
    # Erweiterte indische Keywords
    indian_keywords = [
        'cricket', 'bollywood', 'hindi', 'india', 'indian', 'mumbai', 'delhi',
        'singh', 'kumar', 'sharma', 'patel', 'gupta', 'raj', 'amit', 'rohit',
        'ipl', 'csk', 'mi', 'rcb', 'subscribe karo', 'like kijiye', 'tamil',
        'telugu', 'malayalam', 'bengali', 'punjabi', 'bhojpuri', 'desi',
        'viral video', 'funny video', 'crore', 'lakh', 'rupees'
    ]
    
    indian_count = sum(1 for keyword in indian_keywords if keyword in text)
    
    if target_region != 'IN':
        if indian_count >= 3:
            confidence_score -= 0.5  # Sehr starke Reduktion
            print(f"🚫 V5.0: Sehr starke indische Indikatoren: {indian_count}")
        elif indian_count >= 2:
            confidence_score -= 0.35  # Starke Reduktion
            print(f"🚫 V5.0: Starke indische Indikatoren: {indian_count}")
        elif indian_count >= 1:
            confidence_score -= 0.2   # Mittlere Reduktion
            print(f"⚠️ V5.0: Indische Indikatoren: {indian_count}")
    
    # 3. V5.0 Views-to-Age Ratio
    views_per_hour = views / max(age_hours, 1)
    if views_per_hour > 50000:    # Viral
        confidence_score += 0.25
    elif views_per_hour > 10000:  # Sehr gut
        confidence_score += 0.15
    elif views_per_hour > 1000:   # Gut
        confidence_score += 0.1
    elif views_per_hour < 50:     # Sehr langsam
        confidence_score -= 0.1
    
    # 4. V5.0 Enhanced Regionale Inhalte bevorzugen
    if target_region == 'DE':
        german_keywords = [
            'deutschland', 'german', 'deutsch', 'bundesliga', 'münchen', 'berlin', 
            'hamburg', 'dazn', 'sport1', 'ard', 'zdf', 'bayern', 'dortmund'
        ]
        german_count = sum(1 for keyword in german_keywords if keyword in text)
        if german_count >= 2:
            confidence_score += 0.3
            print(f"✅ V5.0: Starke deutsche Indikatoren: {german_count}")
        elif german_count >= 1:
            confidence_score += 0.2
            print(f"✅ V5.0: Deutsche Indikatoren: {german_count}")
    
    elif target_region == 'US':
        us_keywords = ['america', 'american', 'usa', 'nfl', 'nba', 'mlb', 'espn', 'cnn']
        us_count = sum(1 for keyword in us_keywords if keyword in text)
        if us_count >= 1:
            confidence_score += 0.25
    
    elif target_region == 'ES':
        spanish_keywords = ['españa', 'spanish', 'madrid', 'barcelona', 'la liga', 'real madrid']
        spanish_count = sum(1 for keyword in spanish_keywords if keyword in text)
        if spanish_count >= 1:
            confidence_score += 0.25
    
    # V5.0: Realistischer Bereich (10% - 95%)
    final_confidence = max(0.10, min(0.95, confidence_score))
    
    return final_confidence
