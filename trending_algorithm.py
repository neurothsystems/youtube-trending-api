# OPTIMIZED trending_algorithm.py - Verbesserte Score-Formel basierend auf User-Feedback
"""
OPTIMIZED Trending Algorithm mit verbesserter Score-Berechnung:

FIXES von User-Feedback:
- Views: 75% Gewichtung (Haupttreiber)
- Comments: Moderate Gewichtung (8x Faktor)  
- Likes: Moderate Gewichtung (2x Faktor)
- Alter: Linearer Einfluss statt exponentieller Penalty
- Dauer: KEIN Bonus mehr (verhindert Livestream-Dominanz)
- Frische-Boost: Nur 10% für <12h Videos
"""

import math
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# [Alle anderen Klassen bleiben gleich - VideoData, TrendingResult, etc.]
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
    algorithm_version: str = "optimized_v7.0"
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


class OptimizedTrendingAlgorithm(TrendingAlgorithm):
    """
    OPTIMIZED Trending-Algorithmus basierend auf User-Feedback
    
    Verbesserungen:
    - Views: 75% Gewichtung (Haupttreiber für Trends)
    - Comments: 8x Faktor (wertvoll aber seltener als Likes)
    - Likes: 2x Faktor (moderate Gewichtung)
    - Linearer Age-Einfluss statt exponentieller Penalty
    - KEIN Duration-Bonus (verhindert Livestream-Bias)
    - Frische-Boost: Max 10% für Videos <12h
    """
    
    def __init__(self, 
                 views_weight: float = 0.75,
                 comments_factor: float = 8.0,
                 likes_factor: float = 2.0,
                 freshness_boost_hours: float = 12.0,
                 max_freshness_boost: float = 0.1,
                 min_age_hours: float = 2.0):
        """
        OPTIMIZED Algorithm Parameters
        
        Args:
            views_weight: Gewichtung für Views (empfohlen: 0.75 = 75%)
            comments_factor: Multiplikator für Comments (empfohlen: 8.0)
            likes_factor: Multiplikator für Likes (empfohlen: 2.0)
            freshness_boost_hours: Unter X Stunden gibt es Frische-Boost (empfohlen: 12h)
            max_freshness_boost: Maximaler Frische-Boost (empfohlen: 0.1 = 10%)
            min_age_hours: Minimum Age für Division (verhindert Division durch ~0)
        """
        self.views_weight = views_weight
        self.comments_factor = comments_factor
        self.likes_factor = likes_factor
        self.freshness_boost_hours = freshness_boost_hours
        self.max_freshness_boost = max_freshness_boost
        self.min_age_hours = min_age_hours
        self.version = "optimized_v7.0"
        
        print(f"🚀 OPTIMIZED Algorithm V7.0 initialized:")
        print(f"   Views weight: {views_weight}")
        print(f"   Comments factor: {comments_factor}x")
        print(f"   Likes factor: {likes_factor}x")
        print(f"   Freshness boost: {max_freshness_boost*100}% for <{freshness_boost_hours}h videos")
        print(f"   NO duration bonus (Livestream-bias eliminated)")
    
    def calculate_trending_score(self, video: VideoData) -> float:
        """
        OPTIMIZED Trending-Score-Berechnung
        
        Formel:
        1. Basis: (Views * 0.75 + Comments * 8 + Likes * 2) / age_hours
        2. Frische-Boost: +10% für Videos <12h (linear abfallend)
        3. KEIN Duration-Bonus mehr!
        """
        
        # Basis-Metriken extrahieren
        views = max(video.views, 1)
        comments = video.comments
        likes = video.likes
        age_hours = max(video.age_hours, self.min_age_hours)  # Mindestens 2h
        
        # OPTIMIZED: Neue Score-Berechnung basierend auf User-Feedback
        raw_score = (
            views * self.views_weight +           # 75% Views (Haupttreiber)
            comments * self.comments_factor +    # Comments * 8 (wertvoll aber selten)
            likes * self.likes_factor             # Likes * 2 (moderate Gewichtung)
        )
        
        # Pro-Zeit-Normalisierung (VIEL besser als exponentieller Penalty)
        score_per_hour = raw_score / age_hours
        
        # OPTIMIZED: Frische-Boost für neue Videos (max 10%, linear abfallend)
        freshness_multiplier = 1.0
        if video.age_hours < self.freshness_boost_hours:
            # Linearer Boost: 10% für 0h → 0% für 12h
            boost_percentage = self.max_freshness_boost * (
                (self.freshness_boost_hours - video.age_hours) / self.freshness_boost_hours
            )
            freshness_multiplier = 1.0 + boost_percentage
        
        # Finaler Score (OHNE Duration-Bonus!)
        final_score = score_per_hour * freshness_multiplier
        
        # Debug-Output für Optimierung
        if video.age_hours < 1:  # Nur für sehr neue Videos loggen
            print(f"🔍 OPTIMIZED Score Debug: {video.title[:30]}...")
            print(f"   Views: {views:,} * {self.views_weight} = {views * self.views_weight:,.0f}")
            print(f"   Comments: {comments:,} * {self.comments_factor} = {comments * self.comments_factor:,.0f}")
            print(f"   Likes: {likes:,} * {self.likes_factor} = {likes * self.likes_factor:,.0f}")
            print(f"   Raw Score: {raw_score:,.0f}")
            print(f"   Age: {age_hours:.1f}h → Per Hour: {score_per_hour:,.0f}")
            print(f"   Freshness: {freshness_multiplier:.3f}x")
            print(f"   Final: {final_score:,.0f}")
        
        return final_score
    
    def calculate_trending_score_with_regional_boost(self, video: VideoData, regional_relevance_score: float = 0.0) -> float:
        """
        OPTIMIZED Score mit Regional-Boost
        
        Args:
            video: Video-Daten
            regional_relevance_score: Regional-Relevance (0.0-1.0)
            
        Returns:
            Final Trending-Score mit Regional-Boost
        """
        
        # Basis-Score berechnen
        base_score = self.calculate_trending_score(video)
        
        # Regional-Boost anwenden (max +20%)
        regional_multiplier = 1.0 + (regional_relevance_score * 0.2)
        boosted_score = base_score * regional_multiplier
        
        # Debug für Regional-Boost
        if regional_relevance_score > 0.5:
            print(f"🎯 Regional Boost: {video.title[:30]}...")
            print(f"   Base Score: {base_score:,.0f}")
            print(f"   Regional Relevance: {regional_relevance_score:.2f}")
            print(f"   Boost: +{(regional_multiplier-1)*100:.1f}%")
            print(f"   Final: {boosted_score:,.0f}")
        
        return boosted_score
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Algorithmus-Informationen für API"""
        return {
            "version": self.version,
            "description": "OPTIMIZED Algorithm basierend auf User-Feedback",
            "improvements": [
                "Views: 75% Gewichtung (Haupttreiber)",
                "Comments: 8x Faktor (wertvoll aber selten)",
                "Likes: 2x Faktor (moderate Gewichtung)", 
                "Linearer Age-Einfluss (kein exponentieller Penalty)",
                "KEIN Duration-Bonus (eliminiert Livestream-Bias)",
                "Frische-Boost: 10% für <12h Videos"
            ],
            "parameters": {
                "views_weight": self.views_weight,
                "comments_factor": self.comments_factor,
                "likes_factor": self.likes_factor,
                "freshness_boost_hours": self.freshness_boost_hours,
                "max_freshness_boost": self.max_freshness_boost,
                "duration_bonus": "REMOVED (was causing Livestream bias)"
            },
            "formula": "(Views*0.75 + Comments*8 + Likes*2) / age_hours * freshness_boost",
            "benefits": [
                "Transparenter und verständlicher",
                "Weniger anfällig für Bot-Manipulation",
                "Bessere Balance zwischen neuen und etablierten Videos",
                "Eliminiert Livestream-Dominanz",
                "Realistische Trend-Erkennung"
            ]
        }


# OPTIMIZED: Legacy-Kompatibilität mit verbessertem Algorithmus
class EnhancedTrendingAlgorithm(OptimizedTrendingAlgorithm):
    """Alias für Backwards-Compatibility"""
    
    def __init__(self, engagement_factor: float = 8.0, freshness_exponent: float = 1.0):
        """
        Legacy-Constructor für Kompatibilität
        
        Args:
            engagement_factor: Wird für comments_factor verwendet
            freshness_exponent: Wird ignoriert (linearer Einfluss ist besser)
        """
        # Konvertiere alte Parameter zu neuen
        super().__init__(
            views_weight=0.75,
            comments_factor=engagement_factor,
            likes_factor=2.0,
            freshness_boost_hours=12.0,
            max_freshness_boost=0.1
        )
        print(f"🔄 Legacy compatibility: engagement_factor={engagement_factor} → comments_factor={engagement_factor}")
        print(f"🔄 Legacy compatibility: freshness_exponent={freshness_exponent} → IGNORED (using linear age influence)")


# OPTIMIZED: V6 Analyzer mit verbessertem Algorithmus
class V6TrendingAnalyzer:
    """V6.1 Analyzer mit OPTIMIZED Algorithm"""
    
    def __init__(self, algorithm: TrendingAlgorithm = None, target_region: str = "DE"):
        """Initialize mit OPTIMIZED Algorithm als Default"""
        self.target_region = target_region
        
        # OPTIMIZED: Verwende neuen Algorithmus als Standard
        if algorithm is None:
            self.algorithm = OptimizedTrendingAlgorithm()
            print("🚀 Using OPTIMIZED Algorithm V7.0 (User-Feedback based)")
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
        OPTIMIZED Video-Analyse mit verbessertem Algorithmus
        """
        
        # Duration-Filter anwenden
        if min_duration > 0:
            min_duration_seconds = min_duration * 60
            videos = [v for v in videos if v.duration_seconds >= min_duration_seconds]
            print(f"🔧 Duration-Filter: {len(videos)} Videos ≥ {min_duration} Minuten")
        
        print(f"\n🚀 OPTIMIZED Analysis: '{query}' → {self.target_region}")
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
                
                # OPTIMIZED: Neue Score-Berechnung mit Regional-Boost
                if isinstance(self.algorithm, OptimizedTrendingAlgorithm):
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
                    algorithm_version="optimized_v7.0",
                    regional_relevance=regional_relevance,
                    blacklisted=regional_relevance.get('blacklisted', False)
                )
                
                results.append(result)
                
            except Exception as e:
                print(f"⚠️ Error analyzing video {video.video_id}: {e}")
                continue
        
        # OPTIMIZED: Sortierung nach Trending-Score (korrekt)
        results.sort(key=lambda x: x.trending_score, reverse=True)
        
        # OPTIMIZED: Korrekte normalized_score Berechnung
        if results:
            max_score = results[0].trending_score
            for idx, result in enumerate(results[:top_count]):
                result.rank = idx + 1
                result.normalized_score = min((result.trending_score / max_score) * 10, 10.0)
        
        # Debug-Output
        print(f"📊 OPTIMIZED Results:")
        print(f"   Total analyzed: {len(results)}")
        if len(results) >= 3:
            print(f"   Top 3 Scores: {results[0].trending_score:.0f}, {results[1].trending_score:.0f}, {results[2].trending_score:.0f}")
        print("=" * 60)
        
        # Legacy filter_stats für Kompatibilität
        filter_stats = {
            "original_count": len(videos),
            "algorithm_used": "optimized_v7.0",
            "improvements_applied": [
                "Linear age influence",
                "No duration bias", 
                "Optimized engagement weighting",
                "Improved freshness boost"
            ]
        }
        
        return results[:top_count], filter_stats
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Algorithm-Info für API"""
        base_info = self.algorithm.get_algorithm_info()
        base_info.update({
            "analyzer_version": "v6.1_optimized",
            "target_region": self.target_region,
            "optimization_source": "User feedback based improvements"
        })
        return base_info


# Compatibility Aliases
TrendingAnalyzer = V6TrendingAnalyzer
V5TrendingAnalyzer = V6TrendingAnalyzer


# OPTIMIZED Algorithm Factory
class AlgorithmFactory:
    """Factory mit OPTIMIZED Algorithm als Standard"""
    
    @staticmethod
    def create_basic_algorithm() -> TrendingAlgorithm:
        """Basis-Algorithmus (jetzt OPTIMIZED)"""
        return OptimizedTrendingAlgorithm()
    
    @staticmethod
    def create_regional_algorithm(region: str) -> TrendingAlgorithm:
        """Regional-optimierter Algorithmus"""
        return OptimizedTrendingAlgorithm(
            views_weight=0.75,
            comments_factor=8.0,
            likes_factor=2.0,
            freshness_boost_hours=12.0,
            max_freshness_boost=0.15  # Leicht höherer Boost für regionale Algorithmen
        )
    
    @staticmethod
    def create_anti_spam_algorithm() -> TrendingAlgorithm:
        """Anti-Spam-Algorithmus"""
        return OptimizedTrendingAlgorithm(
            views_weight=0.80,        # Mehr Gewicht auf Views (schwerer zu faken)
            comments_factor=6.0,      # Weniger Gewicht auf Comments (leichter zu faken)
            likes_factor=1.5,         # Weniger Gewicht auf Likes
            freshness_boost_hours=6.0, # Kürzerer Freshness-Boost
            max_freshness_boost=0.05   # Geringerer Boost (verhindert schnelle Manipulation)
        )
    
    @staticmethod
    def create_experimental_algorithm() -> TrendingAlgorithm:
        """Experimenteller Algorithmus für Tests"""
        return OptimizedTrendingAlgorithm(
            views_weight=0.70,
            comments_factor=10.0,     # Höhere Comment-Gewichtung
            likes_factor=3.0,         # Höhere Like-Gewichtung
            freshness_boost_hours=24.0, # Längerer Freshness-Boost
            max_freshness_boost=0.20   # Höherer Boost
        )


# OPTIMIZED: Test-Funktion
def test_optimized_algorithm():
    """Test der OPTIMIZED Algorithm-Verbesserungen"""
    
    print("\n🧪 TESTING OPTIMIZED Algorithm V7.0")
    print("=" * 50)
    
    # Test-Videos erstellen
    test_videos = [
        # Altes populäres Video
        VideoData("old_popular", "Altes populäres Video", "TestChannel", 
                 views=1000000, comments=5000, likes=50000, 
                 duration_seconds=600, age_hours=48, published_at=""),
        
        # Neues viral Video  
        VideoData("new_viral", "Neues virales Video", "TestChannel",
                 views=500000, comments=8000, likes=40000,
                 duration_seconds=300, age_hours=6, published_at=""),
        
        # Livestream (sollte KEINEN Duration-Bonus bekommen)
        VideoData("livestream", "Langer Livestream", "TestChannel",
                 views=200000, comments=3000, likes=15000,
                 duration_seconds=10800, age_hours=12, published_at="")  # 3h Livestream
    ]
    
    # Algorithmen vergleichen
    old_algorithm = EnhancedTrendingAlgorithm(engagement_factor=10.0, freshness_exponent=1.3)
    new_algorithm = OptimizedTrendingAlgorithm()
    
    print("\nVergleich OLD vs OPTIMIZED:")
    print("-" * 30)
    
    for video in test_videos:
        old_score = old_algorithm.calculate_trending_score(video)
        new_score = new_algorithm.calculate_trending_score(video)
        
        print(f"\n{video.title}:")
        print(f"  Views: {video.views:,}, Comments: {video.comments:,}, Age: {video.age_hours}h")
        print(f"  OLD Score: {old_score:,.0f}")
        print(f"  NEW Score: {new_score:,.0f}")
        print(f"  Difference: {((new_score/old_score)-1)*100:+.1f}%")


if __name__ == "__main__":
    # Test die Optimierungen
    test_optimized_algorithm()
