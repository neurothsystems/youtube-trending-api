# trending_algorithm.py - KOMPLETTE DATEI mit Confidence-Fix
"""
Modularer YouTube Trending Algorithmus mit verbesserter regionaler Filterung
Einfach austauschbar und testbar für verschiedene Strategien
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


class RegionalFilter:
    """Verbesserte regionale Filterung"""
    
    # Sprach-Erkennungs-Patterns
    LANGUAGE_PATTERNS = {
        'hindi': [
            'hindi', 'bollywood', 'desi', 'bhojpuri', 'punjabi',
            'tamil', 'telugu', 'malayalam', 'bengali', 'gujarati', 'marathi'
        ],
        'german': [
            'deutsch', 'deutschland', 'österreich', 'schweiz', 'wien', 'berlin',
            'münchen', 'hamburg', 'köln', 'frankfurt'
        ],
        'spanish': [
            'español', 'españa', 'mexico', 'argentina', 'colombia', 'madrid',
            'barcelona', 'valencia', 'sevilla'
        ],
        'french': [
            'français', 'france', 'paris', 'lyon', 'marseille', 'toulouse',
            'québec', 'montreal', 'belge', 'suisse'
        ],
        'english': [
            'english', 'america', 'american', 'british', 'london', 'new york',
            'los angeles', 'chicago', 'houston'
        ]
    }
    
    # Indische Namen/Kanäle (häufige Patterns)
    INDIAN_PATTERNS = [
        r'\b(singh|kumar|sharma|patel|gupta|agarwal|jain|yadav)\b',
        r'\b(raj|dev|ved|aman|rohit|amit|suresh|ramesh)\b',
        r'\b(bollywood|hindi|desi|bhojpuri|punjabi)\b',
        r'\b(india|indian|hindi|tamil|telugu)\b'
    ]
    
    @classmethod
    def detect_content_language(cls, video: VideoData) -> Optional[str]:
        """Erkenne die wahrscheinliche Sprache des Videos"""
        text = f"{video.title} {video.channel}".lower()
        
        scores = {}
        for language, patterns in cls.LANGUAGE_PATTERNS.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                scores[language] = score
        
        if not scores:
            return None
            
        return max(scores, key=scores.get)
    
    @classmethod
    def detect_indian_content(cls, video: VideoData) -> Tuple[bool, float]:
        """Erweiterte Erkennung indischer Inhalte mit Confidence-Score"""
        text = f"{video.title} {video.channel}".lower()
        
        # Pattern-basierte Erkennung
        pattern_matches = sum(
            1 for pattern in cls.INDIAN_PATTERNS
            if re.search(pattern, text, re.IGNORECASE)
        )
        
        # Engagement-Pattern (indische Videos haben oft sehr hohe Comment-Raten)
        engagement_rate = video.comments / max(video.views, 1)
        high_engagement = engagement_rate > 0.03  # >3% Comment-Rate
        
        # Channel-Name-Pattern
        channel_indian = any(
            re.search(pattern, video.channel, re.IGNORECASE)
            for pattern in cls.INDIAN_PATTERNS
        )
        
        # Title-Language-Detection
        title_indian = any(
            keyword in text
            for keyword in cls.LANGUAGE_PATTERNS['hindi']
        )
        
        # Berechne Confidence-Score
        indicators = [
            pattern_matches > 0,
            high_engagement,
            channel_indian,
            title_indian
        ]
        
        confidence = sum(indicators) / len(indicators)
        is_indian = confidence >= 0.5
        
        return is_indian, confidence


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
    """Regional optimierter Algorithmus gegen indische Video-Dominanz"""
    
    def __init__(self, target_region: str = "DE", **kwargs):
        super().__init__(**kwargs)
        self.target_region = target_region
        self.version = "regional_v3.0"
    
    def calculate_trending_score(self, video: VideoData) -> float:
        """Regional optimierte Score-Berechnung"""
        
        # Basis-Score berechnen
        base_score = super().calculate_trending_score(video)
        
        # Regionale Anpassungen
        if self.target_region and self.target_region != 'IN':
            is_indian, confidence = RegionalFilter.detect_indian_content(video)
            
            if is_indian:
                # Reduziere indische Videos stark in anderen Regionen
                penalty = 0.1 + (0.4 * (1 - confidence))  # 10-50% vom Original-Score
                base_score *= penalty
        
        # Sprach-Boost für Zielregion
        detected_language = RegionalFilter.detect_content_language(video)
        if detected_language:
            language_boost = self._get_language_boost(detected_language)
            base_score *= language_boost
        
        return base_score
    
    def _get_language_boost(self, detected_language: str) -> float:
        """Sprach-Boost basierend auf Zielregion"""
        boost_map = {
            'DE': {'german': 1.8, 'english': 1.2, 'french': 1.1, 'hindi': 0.3},
            'US': {'english': 1.5, 'spanish': 1.2, 'hindi': 0.4},
            'ES': {'spanish': 1.8, 'english': 1.2, 'hindi': 0.3},
            'FR': {'french': 1.8, 'english': 1.2, 'hindi': 0.3},
            'GB': {'english': 1.8, 'hindi': 0.4}
        }
        
        if self.target_region in boost_map:
            return boost_map[self.target_region].get(detected_language, 1.0)
        
        return 1.0
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        info = super().get_algorithm_info()
        info.update({
            "target_region": self.target_region,
            "regional_features": [
                "Anti-Indian-Bias",
                "Language-Detection",
                "Regional-Boost",
                "Content-Origin-Filtering"
            ]
        })
        return info


class TrendingAnalyzer:
    """Haupt-Analyzer-Klasse"""
    
    def __init__(self, algorithm: TrendingAlgorithm):
        self.algorithm = algorithm
    
    def analyze_videos(self, 
                      videos: List[VideoData], 
                      top_count: int = 12,
                      min_score: float = 0.0) -> List[TrendingResult]:
        """Analysiere Videos und erstelle Ranking"""
        
        results = []
        
        for video in videos:
            # Berechne Trending-Score
            trending_score = self.algorithm.calculate_trending_score(video)
            
            # Skip Videos unter Mindest-Score
            if trending_score < min_score:
                continue
            
            results.append(TrendingResult(
                video_data=video,
                trending_score=trending_score,
                rank=0,  # Wird später gesetzt
                normalized_score=0.0,  # Wird später berechnet
                algorithm_version=self.algorithm.version if hasattr(self.algorithm, 'version') else "unknown"
            ))
        
        # Sortiere nach Trending-Score
        results.sort(key=lambda x: x.trending_score, reverse=True)
        
        # Setze Rankings und normalisierte Scores
        top_score = results[0].trending_score if results else 1.0
        
        for i, result in enumerate(results[:top_count], 1):
            result.rank = i
            result.normalized_score = (result.trending_score / top_score) * 10
        
        return results[:top_count]
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Informationen über den verwendeten Algorithmus"""
        return self.algorithm.get_algorithm_info()


# Vordefinierte Algorithmus-Strategien
class AlgorithmFactory:
    """Factory für verschiedene Algorithmus-Strategien"""
    
    @staticmethod
    def create_basic_algorithm() -> TrendingAlgorithm:
        """Basis-Algorithmus ohne regionale Optimierung"""
        return EnhancedTrendingAlgorithm()
    
    @staticmethod
    def create_regional_algorithm(region: str) -> TrendingAlgorithm:
        """Regional optimierter Algorithmus"""
        return RegionalOptimizedAlgorithm(target_region=region)
    
    @staticmethod
    def create_anti_spam_algorithm() -> TrendingAlgorithm:
        """Anti-Spam optimierter Algorithmus"""
        return EnhancedTrendingAlgorithm(
            engagement_factor=8.0,
            anti_spam_threshold=0.02,
            freshness_exponent=1.5
        )


# NEU: CONFIDENCE-BERECHNUNG (das war das fehlende Stück!)
def calculate_realistic_confidence(video_title, video_channel, views, comments, age_hours, target_region='DE'):
    """
    Berechnet realistische Confidence-Werte statt 50% Default
    Diese Funktion war der Grund für die 50% Confidence überall!
    """
    confidence_score = 0.5  # Start bei 50%
    
    # 1. Engagement-Check
    engagement_rate = comments / max(views, 1)
    if engagement_rate > 0.05:  # >5% = sehr verdächtig (Bots)
        confidence_score -= 0.3
    elif engagement_rate > 0.02:  # 2-5% = etwas verdächtig
        confidence_score -= 0.1
    elif engagement_rate >= 0.001:  # 0.1-2% = gesund
        confidence_score += 0.2
    
    # 2. Verstärkter Indien-Check
    text = f"{video_title} {video_channel}".lower()
    indian_keywords = [
        'cricket', 'bollywood', 'hindi', 'india', 'indian', 'mumbai', 'delhi',
        'singh', 'kumar', 'sharma', 'patel', 'gupta', 'raj', 'amit', 'rohit',
        'ipl', 'csk', 'mi', 'rcb', 'subscribe karo', 'like kijiye', 'tamil',
        'telugu', 'malayalam', 'bengali', 'punjabi', 'bhojpuri', 'desi'
    ]
    
    indian_count = sum(1 for keyword in indian_keywords if keyword in text)
    
    if target_region != 'IN' and indian_count >= 2:
        confidence_score -= 0.4  # Starke Reduktion für indische Inhalte
        print(f"🚫 Starke indische Indikatoren gefunden: {indian_count}")
    elif target_region != 'IN' and indian_count >= 1:
        confidence_score -= 0.2  # Mittlere Reduktion
        print(f"⚠️ Indische Indikatoren gefunden: {indian_count}")
    
    # 3. Views-to-Age Ratio
    views_per_hour = views / max(age_hours, 1)
    if views_per_hour > 10000:  # Viral
        confidence_score += 0.2
    elif views_per_hour > 1000:  # Gut
        confidence_score += 0.1
    elif views_per_hour < 50:    # Sehr langsam
        confidence_score -= 0.1
    
    # 4. Regionale Inhalte bevorzugen
    if target_region == 'DE':
        german_keywords = ['deutschland', 'german', 'deutsch', 'bundesliga', 'münchen', 'berlin', 'hamburg', 'dazn', 'sport1']
        german_count = sum(1 for keyword in german_keywords if keyword in text)
        if german_count >= 1:
            confidence_score += 0.2
            print(f"✅ Deutsche Indikatoren gefunden: {german_count}")
    elif target_region == 'US':
        us_keywords = ['america', 'american', 'usa', 'nfl', 'nba', 'mlb', 'espn']
        us_count = sum(1 for keyword in us_keywords if keyword in text)
        if us_count >= 1:
            confidence_score += 0.2
    elif target_region == 'ES':
        spanish_keywords = ['españa', 'spanish', 'madrid', 'barcelona', 'la liga']
        spanish_count = sum(1 for keyword in spanish_keywords if keyword in text)
        if spanish_count >= 1:
            confidence_score += 0.2
    
    # Auf realistischen Bereich begrenzen (15% - 90%)
    final_confidence = max(0.15, min(0.90, confidence_score))
    
    return final_confidence


# Demo/Test-Funktionen
def test_algorithm():
    """Test verschiedener Algorithmen"""
    
    # Test-Video-Daten
    test_videos = [
        VideoData(
            video_id="test1",
            title="Amazing Tech Review 2025",
            channel="TechGuru DE",
            views=100000,
            comments=500,
            likes=8000,
            duration_seconds=600,
            age_hours=12,
            published_at="2025-07-12T12:00:00Z"
        ),
        VideoData(
            video_id="test2",
            title="Bollywood Dance Performance Hindi",
            channel="Raj Kumar Entertainment",
            views=50000,
            comments=2500,  # Hohe Comment-Rate (5%)
            likes=3000,
            duration_seconds=240,
            age_hours=8,
            published_at="2025-07-12T16:00:00Z"
        )
    ]
    
    # Teste verschiedene Algorithmen
    algorithms = {
        "Basic": AlgorithmFactory.create_basic_algorithm(),
        "Regional DE": AlgorithmFactory.create_regional_algorithm("DE"),
        "Anti-Spam": AlgorithmFactory.create_anti_spam_algorithm()
    }
    
    for name, algorithm in algorithms.items():
        analyzer = TrendingAnalyzer(algorithm)
        results = analyzer.analyze_videos(test_videos)
        
        print(f"\n=== {name} Algorithm ===")
        for result in results:
            print(f"#{result.rank}: {result.video_data.title}")
            print(f"  Score: {result.trending_score:.2f} | Normalized: {result.normalized_score:.1f}/10")
            
            # Teste indische Erkennung
            is_indian, confidence = RegionalFilter.detect_indian_content(result.video_data)
            print(f"  Indian Content: {is_indian} (Confidence: {confidence:.2f})")


if __name__ == "__main__":
    test_algorithm()
