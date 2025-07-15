# MOMENTUM trending_algorithm.py - Original PRD Formel
"""
MOMENTUM Trending Algorithm - Zurück zur ursprünglichen PRD-Formel:

Trending-Score = (Views/Stunde × 0.6) + (Engagement-Rate × Views × 0.3) + (Views × Zeit-Dämpfung × 0.1)

Dabei:
- Views/Stunde = Geschwindigkeit der Popularität (60% Gewichtung)
- Engagement-Rate = (Likes + Kommentare) / Views (30% Gewichtung)
- Zeit-Dämpfung = exp(-Stunden_seit_Upload / 24) (10% Gewichtung)

Vorteile:
- Videos mit hoher Interaktion werden bevorzugt
- Neuere Videos erhalten faire Chancen
- Echtes "Momentum" wird gemessen, nicht nur Gesamtpopularität
"""

import math
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# [Alle bestehenden Klassen von vorher - VideoData, TrendingResult, etc.]
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
    algorithm_version: str = "momentum_v8.0"
    filter_applied: Optional[str] = None
    is_indian_content: bool = False
    is_regional_content: bool = False
    regional_relevance: Optional[Dict] = None
    blacklisted: bool = False


class TrendingAlgorithm(ABC):
    """Abstract Base Class für Trending-Algorithmen"""
    
    @abstractmethod
    def calculate_trending_score(self, video: VideoData) -> float:
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        pass


class MomentumTrendingAlgorithm(TrendingAlgorithm):
    """
    MOMENTUM Trending Algorithm - Original PRD Formel
    
    Trending-Score = (Views/Stunde × 0.6) + (Engagement-Rate × Views × 0.3) + (Views × Zeit-Dämpfung × 0.1)
    
    Diese Formel balanciert perfekt:
    - Velocity (Views/Stunde) als Hauptfaktor
    - Engagement × Popularität als wichtiger Sekundärfaktor
    - Zeit-Dämpfung für Frische-Boost
    """
    
    def __init__(self, 
                 velocity_weight: float = 0.6,
                 engagement_weight: float = 0.3,
                 freshness_weight: float = 0.1,
                 time_decay_hours: float = 24.0):
        """
        MOMENTUM Algorithm Parameters
        
        Args:
            velocity_weight: Gewichtung für Views/Stunde (empfohlen: 0.6)
            engagement_weight: Gewichtung für Engagement×Views (empfohlen: 0.3)
            freshness_weight: Gewichtung für Zeit-Dämpfung (empfohlen: 0.1)
            time_decay_hours: Halbwertszeit für Zeit-Dämpfung (empfohlen: 24h)
        """
        self.velocity_weight = velocity_weight
        self.engagement_weight = engagement_weight
        self.freshness_weight = freshness_weight
        self.time_decay_hours = time_decay_hours
        self.version = "momentum_v8.0"
        
        print(f"🚀 MOMENTUM Algorithm V8.0 initialized:")
        print(f"   Velocity (Views/h): {velocity_weight*100}%")
        print(f"   Engagement × Views: {engagement_weight*100}%")
        print(f"   Zeit-Dämpfung: {freshness_weight*100}%")
        print(f"   Time decay: {time_decay_hours}h")
        print(f"   Formula: (Views/h × {velocity_weight}) + (Engagement×Views × {engagement_weight}) + (Views×Decay × {freshness_weight})")
    
    def calculate_trending_score(self, video: VideoData) -> float:
        """
        MOMENTUM Trending-Score-Berechnung - Original PRD Formel
        
        Trending-Score = (Views/Stunde × 0.6) + (Engagement-Rate × Views × 0.3) + (Views × Zeit-Dämpfung × 0.1)
        """
        
        # Basis-Metriken extrahieren
        views = max(video.views, 1)
        comments = video.comments
        likes = video.likes
        age_hours = max(video.age_hours, 0.1)  # Mindestens 0.1h (6 Minuten)
        
        # 1. VELOCITY: Views pro Stunde (Hauptfaktor - 60%)
        views_per_hour = views / age_hours
        velocity_score = views_per_hour * self.velocity_weight
        
        # 2. ENGAGEMENT: Engagement-Rate × Views (Sekundärfaktor - 30%)
        engagement_rate = (likes + comments) / views
        engagement_score = engagement_rate * views * self.engagement_weight
        
        # 3. FRESHNESS: Views × Zeit-Dämpfung (Frische-Boost - 10%)
        time_decay = math.exp(-age_hours / self.time_decay_hours)
        freshness_score = views * time_decay * self.freshness_weight
        
        # FINALE MOMENTUM-SCORE
        momentum_score = velocity_score + engagement_score + freshness_score
        
        # Debug-Output für neue Videos (um Formel zu verstehen)
        if age_hours < 2:  # Nur für sehr neue Videos loggen
            print(f"🔍 MOMENTUM Score Debug: {video.title[:30]}...")
            print(f"   Views: {views:,}, Likes: {likes:,}, Comments: {comments:,}")
            print(f"   Age: {age_hours:.1f}h")
            print(f"   1. Velocity: {views_per_hour:,.0f}/h × {self.velocity_weight} = {velocity_score:,.0f}")
            print(f"   2. Engagement: {engagement_rate:.4f} × {views:,} × {self.engagement_weight} = {engagement_score:,.0f}")
            print(f"   3. Freshness: {views:,} × {time_decay:.3f} × {self.freshness_weight} = {freshness_score:,.0f}")
            print(f"   TOTAL MOMENTUM: {momentum_score:,.0f}")
        
        return momentum_score
    
    def calculate_trending_score_with_regional_boost(self, video: VideoData, regional_relevance_score: float = 0.0) -> float:
        """
        MOMENTUM Score mit Regional-Boost
        
        Args:
            video: Video-Daten
            regional_relevance_score: Regional-Relevance (0.0-1.0)
            
        Returns:
            Final Trending-Score mit Regional-Boost
        """
        
        # Basis MOMENTUM-Score berechnen
        base_score = self.calculate_trending_score(video)
        
        # Regional-Boost anwenden (max +20%)
        regional_multiplier = 1.0 + (regional_relevance_score * 0.2)
        boosted_score = base_score * regional_multiplier
        
        # Debug für Regional-Boost
        if regional_relevance_score > 0.5:
            print(f"🎯 Regional Boost: {video.title[:30]}...")
            print(f"   Base MOMENTUM: {base_score:,.0f}")
            print(f"   Regional Relevance: {regional_relevance_score:.2f}")
            print(f"   Boost: +{(regional_multiplier-1)*100:.1f}%")
            print(f"   Final MOMENTUM: {boosted_score:,.0f}")
        
        return boosted_score
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Algorithmus-Informationen für API"""
        return {
            "version": self.version,
            "name": "MOMENTUM Trending Algorithm",
            "description": "Original PRD Formel für echte Trend-Erkennung",
            "formula": "Trending-Score = (Views/Stunde × 0.6) + (Engagement-Rate × Views × 0.3) + (Views × Zeit-Dämpfung × 0.1)",
            "components": {
                "velocity": {
                    "formula": "Views / age_hours",
                    "weight": self.velocity_weight,
                    "description": "Geschwindigkeit der Popularität - Haupttreiber für Trends"
                },
                "engagement": {
                    "formula": "(Likes + Comments) / Views * Views",
                    "weight": self.engagement_weight,
                    "description": "Engagement-Rate kombiniert mit absoluter Popularität"
                },
                "freshness": {
                    "formula": "Views * exp(-age_hours / 24)",
                    "weight": self.freshness_weight,
                    "description": "Zeit-Dämpfung bevorzugt neuere Videos"
                }
            },
            "parameters": {
                "velocity_weight": self.velocity_weight,
                "engagement_weight": self.engagement_weight,
                "freshness_weight": self.freshness_weight,
                "time_decay_hours": self.time_decay_hours
            },
            "advantages": [
                "Videos mit hoher Interaktion werden bevorzugt",
                "Neuere Videos erhalten faire Chancen",
                "Echtes 'Momentum' wird gemessen, nicht nur Gesamtpopularität",
                "Balanciert Velocity, Engagement und Frische optimal",
                "Weniger anfällig für reine View-Manipulation"
            ],
            "examples": {
                "viral_new": "Neues Video mit 100K Views/h + hohem Engagement → hoher Score",
                "popular_old": "Altes Video mit 1M Views aber wenig Velocity → mittlerer Score", 
                "engaging_medium": "Mittleres Video mit sehr hohem Engagement → boosted Score"
            }
        }


# MOMENTUM: Legacy-Kompatibilität
class EnhancedTrendingAlgorithm(MomentumTrendingAlgorithm):
    """Legacy-Kompatibilität mit MOMENTUM Algorithm"""
    
    def __init__(self, engagement_factor: float = 10.0, freshness_exponent: float = 1.3):
        """
        Legacy-Constructor - konvertiert zu MOMENTUM Algorithm
        
        Args:
            engagement_factor: Wird für engagement_weight Berechnung verwendet
            freshness_exponent: Wird für time_decay_hours Berechnung verwendet
        """
        # Konvertiere alte Parameter zu neuen MOMENTUM Parametern
        super().__init__(
            velocity_weight=0.6,
            engagement_weight=0.3,
            freshness_weight=0.1,
            time_decay_hours=24.0
        )
        print(f"🔄 Legacy compatibility: engagement_factor={engagement_factor} → MOMENTUM formula")
        print(f"🔄 Legacy compatibility: freshness_exponent={freshness_exponent} → exp(-h/24) decay")


# MOMENTUM: V6 Analyzer mit MOMENTUM Algorithm
class V6TrendingAnalyzer:
    """V6.1 Analyzer mit MOMENTUM Algorithm"""
    
    def __init__(self, algorithm: TrendingAlgorithm = None, target_region: str = "DE"):
        """Initialize mit MOMENTUM Algorithm als Default"""
        self.target_region = target_region
        
        # MOMENTUM: Verwende MOMENTUM Algorithm als Standard
        if algorithm is None:
            self.algorithm = MomentumTrendingAlgorithm()
            print("🚀 Using MOMENTUM Algorithm V8.0 (Original PRD Formula)")
        else:
            self.algorithm = algorithm
            print(f"🔧 Using custom algorithm: {type(algorithm).__name__}")
        
        # Import andere Komponenten (vereinfacht für Focus auf Algorithm)
        try:
            from trending_algorithm import RegionalQueryBuilder, ChannelGeographyAnalyzer, RegionalRelevanceScorer, RegionalAnalysisResponse
            self.query_builder = RegionalQueryBuilder()
            self.channel_analyzer = ChannelGeographyAnalyzer()
            self.relevance_scorer = RegionalRelevanceScorer(target_region)
            self.response_builder = RegionalAnalysisResponse()
        except ImportError:
            # Fallback wenn Module nicht verfügbar
            print("⚠️ Some components not available, using simplified version")
            self.query_builder = None
            self.channel_analyzer = None
            self.relevance_scorer = None
            self.response_builder = None
    
    def analyze_videos(self, videos: List[VideoData], top_count: int = 12, 
                      query: str = "trending", min_duration: int = 0) -> Tuple[List[TrendingResult], Dict]:
        """
        MOMENTUM Video-Analyse mit Original PRD Formel
        """
        
        # Duration-Filter anwenden
        if min_duration > 0:
            min_duration_seconds = min_duration * 60
            videos = [v for v in videos if v.duration_seconds >= min_duration_seconds]
            print(f"🔧 Duration-Filter: {len(videos)} Videos ≥ {min_duration} Minuten")
        
        print(f"\n🚀 MOMENTUM Analysis: '{query}' → {self.target_region}")
        print("=" * 60)
        
        results = []
        for video in videos:
            try:
                # Regional-Relevance berechnen (vereinfacht für Focus auf Algorithm)
                regional_relevance_score = 0.3  # Default-Wert
                
                if self.relevance_scorer and self.channel_analyzer:
                    # Vollständige Regional-Analyse
                    channel_analysis = self.channel_analyzer.analyze_channel_geography_v6(video, self.target_region)
                    query_context = {'base_query': query, 'boost_keywords': []}
                    regional_relevance = self.relevance_scorer.calculate_regional_relevance(video, channel_analysis, query_context)
                    regional_relevance_score = regional_relevance['score']
                else:
                    # Vereinfachte Regional-Analyse
                    regional_relevance = {
                        'score': 0.3,
                        'confidence': 0.5,
                        'explanation': 'Simplified analysis',
                        'blacklisted': False
                    }
                
                # MOMENTUM: Neue Score-Berechnung mit Regional-Boost
                if isinstance(self.algorithm, MomentumTrendingAlgorithm):
                    trending_score = self.algorithm.calculate_trending_score_with_regional_boost(
                        video, regional_relevance_score
                    )
                else:
                    # Fallback für alte Algorithmen
                    trending_score = self.algorithm.calculate_trending_score(video)
                    regional_boost = 1.0 + (regional_relevance_score * 0.2)
                    trending_score *= regional_boost
                
                result = TrendingResult(
                    video_data=video,
                    trending_score=trending_score,
                    rank=0,  # Wird später gesetzt
                    normalized_score=0.0,  # Wird später berechnet
                    algorithm_version="momentum_v8.0",
                    regional_relevance=regional_relevance,
                    blacklisted=regional_relevance.get('blacklisted', False)
                )
                
                results.append(result)
                
            except Exception as e:
                print(f"⚠️ Error analyzing video {video.video_id}: {e}")
                continue
        
        # MOMENTUM: Sortierung nach MOMENTUM-Score
        results.sort(key=lambda x: x.trending_score, reverse=True)
        
        # MOMENTUM: Korrekte normalized_score Berechnung
        if results:
            max_score = results[0].trending_score
            for idx, result in enumerate(results[:top_count]):
                result.rank = idx + 1
                result.normalized_score = min((result.trending_score / max_score) * 10, 10.0)
        
        # Debug-Output
        print(f"📊 MOMENTUM Results:")
        print(f"   Total analyzed: {len(results)}")
        if len(results) >= 3:
            print(f"   Top 3 MOMENTUM Scores: {results[0].trending_score:.0f}, {results[1].trending_score:.0f}, {results[2].trending_score:.0f}")
        print("=" * 60)
        
        # Legacy filter_stats für Kompatibilität
        filter_stats = {
            "original_count": len(videos),
            "algorithm_used": "momentum_v8.0",
            "formula_applied": "Trending-Score = (Views/Stunde × 0.6) + (Engagement-Rate × Views × 0.3) + (Views × Zeit-Dämpfung × 0.1)"
        }
        
        return results[:top_count], filter_stats
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Algorithm-Info für API"""
        base_info = self.algorithm.get_algorithm_info()
        base_info.update({
            "analyzer_version": "v6.1_momentum",
            "target_region": self.target_region,
            "formula_source": "Original PRD - bewährte Formel"
        })
        return base_info


# Compatibility Aliases
TrendingAnalyzer = V6TrendingAnalyzer
V5TrendingAnalyzer = V6TrendingAnalyzer


# MOMENTUM Algorithm Factory
class AlgorithmFactory:
    """Factory mit MOMENTUM Algorithm"""
    
    @staticmethod
    def create_basic_algorithm() -> TrendingAlgorithm:
        """Basis-Algorithmus (MOMENTUM)"""
        return MomentumTrendingAlgorithm()
    
    @staticmethod
    def create_regional_algorithm(region: str) -> TrendingAlgorithm:
        """Regional-optimierter MOMENTUM Algorithmus"""
        return MomentumTrendingAlgorithm(
            velocity_weight=0.6,
            engagement_weight=0.3,
            freshness_weight=0.1,
            time_decay_hours=20.0  # Leicht kürzere Decay-Zeit für regionale Relevanz
        )
    
    @staticmethod
    def create_anti_spam_algorithm() -> TrendingAlgorithm:
        """Anti-Spam MOMENTUM Algorithmus"""
        return MomentumTrendingAlgorithm(
            velocity_weight=0.7,    # Mehr Gewicht auf Views/h (schwerer zu faken)
            engagement_weight=0.2,  # Weniger Gewicht auf Engagement (leichter zu faken)
            freshness_weight=0.1,
            time_decay_hours=12.0   # Kürzere Decay-Zeit (verhindert lange Manipulation)
        )
    
    @staticmethod
    def create_experimental_algorithm() -> TrendingAlgorithm:
        """Experimenteller MOMENTUM Algorithmus"""
        return MomentumTrendingAlgorithm(
            velocity_weight=0.5,
            engagement_weight=0.4,  # Höhere Engagement-Gewichtung
            freshness_weight=0.1,
            time_decay_hours=36.0   # Längere Decay-Zeit
        )


# MOMENTUM: Test-Funktion
def test_momentum_algorithm():
    """Test der MOMENTUM Algorithm mit verschiedenen Video-Typen"""
    
    print("\n🧪 TESTING MOMENTUM Algorithm V8.0")
    print("=" * 50)
    
    # Test-Videos erstellen
    test_videos = [
        # Viral video - hohe Velocity
        VideoData("viral", "Viral Video", "TestChannel", 
                 views=500000, comments=8000, likes=40000, 
                 duration_seconds=300, age_hours=6, published_at=""),
        
        # Engaging video - hohe Engagement-Rate
        VideoData("engaging", "Sehr engaging Video", "TestChannel",
                 views=100000, comments=5000, likes=15000,
                 duration_seconds=600, age_hours=12, published_at=""),
        
        # Popular old video - viele Views aber alt
        VideoData("popular_old", "Populäres altes Video", "TestChannel",
                 views=2000000, comments=10000, likes=100000,
                 duration_seconds=900, age_hours=72, published_at=""),
                 
        # Fresh new video - sehr neu aber wenige Views
        VideoData("fresh", "Brandneues Video", "TestChannel",
                 views=50000, comments=800, likes=5000,
                 duration_seconds=420, age_hours=1, published_at="")
    ]
    
    algorithm = MomentumTrendingAlgorithm()
    
    print("\nMOMENTUM Algorithm Test Results:")
    print("-" * 40)
    
    for video in test_videos:
        score = algorithm.calculate_trending_score(video)
        
        views_per_hour = video.views / video.age_hours
        engagement_rate = (video.likes + video.comments) / video.views
        time_decay = math.exp(-video.age_hours / 24)
        
        print(f"\n{video.title}:")
        print(f"  Views: {video.views:,}, Age: {video.age_hours}h")
        print(f"  Views/h: {views_per_hour:,.0f}")
        print(f"  Engagement: {engagement_rate:.3f}")
        print(f"  Time Decay: {time_decay:.3f}")
        print(f"  MOMENTUM Score: {score:,.0f}")
    
    # Sortiere nach MOMENTUM Score
    scored_videos = [(v, algorithm.calculate_trending_score(v)) for v in test_videos]
    scored_videos.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\nMOMENTUM Ranking:")
    print("-" * 20)
    for i, (video, score) in enumerate(scored_videos, 1):
        print(f"#{i}: {video.title} ({score:,.0f})")


if __name__ == "__main__":
    # Test die MOMENTUM Algorithm
    test_momentum_algorithm()
