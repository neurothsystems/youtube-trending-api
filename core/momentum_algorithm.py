# core/momentum_algorithm.py - V6.0 Clean MOMENTUM Algorithm
"""
MOMENTUM Trending Algorithm - V6.0 Pure Implementation
Basierend auf dem Original PRD aus trending_algorithm.py

Trending-Score = (Views/Stunde × 0.6) + (Engagement-Rate × Views × 0.3) + (Views × Zeit-Dämpfung × 0.1)
"""

import math
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoData:
    """Clean VideoData Structure für V6.0"""
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
    
    # V6.0 Source Tracking
    is_trending_page_video: bool = False
    source: str = 'api'  # 'trending_page' oder 'api'
    region_detected: Optional[str] = None


@dataclass
class TrendingResult:
    """V6.0 Clean Trending Result"""
    video_data: VideoData
    trending_score: float
    rank: int
    normalized_score: float
    confidence: float = 1.0
    
    # V6.0 Enhanced Fields
    is_truly_trending: bool = False
    regional_relevance_score: float = 0.0
    momentum_breakdown: Optional[Dict[str, float]] = None


class MomentumAlgorithm:
    """
    V6.0 MOMENTUM Algorithm - Clean Implementation
    
    Trending-Score = (Views/Stunde × 0.6) + (Engagement×Views × 0.3) + (Views×Zeit-Dämpfung × 0.1)
    
    Optimiert für:
    - Velocity (Views/Stunde) als Haupttreiber
    - Engagement × Popularität als wichtiger Sekundärfaktor  
    - Zeit-Dämpfung für Frische-Boost
    """
    
    def __init__(self, 
                 velocity_weight: float = 0.6,
                 engagement_weight: float = 0.3,
                 freshness_weight: float = 0.1,
                 time_decay_hours: float = 24.0,
                 trending_page_bonus: float = 1.5):
        """
        V6.0 MOMENTUM Algorithm Configuration
        
        Args:
            velocity_weight: Views/Stunde Gewichtung (empfohlen: 0.6)
            engagement_weight: Engagement×Views Gewichtung (empfohlen: 0.3) 
            freshness_weight: Zeit-Dämpfung Gewichtung (empfohlen: 0.1)
            time_decay_hours: Halbwertszeit für Zeit-Dämpfung (empfohlen: 24h)
            trending_page_bonus: Bonus für echte Trending-Videos (empfohlen: 1.5 = +50%)
        """
        self.velocity_weight = velocity_weight
        self.engagement_weight = engagement_weight
        self.freshness_weight = freshness_weight
        self.time_decay_hours = time_decay_hours
        self.trending_page_bonus = trending_page_bonus
        self.version = "momentum_v6.0_clean"
        
        print(f"🚀 MOMENTUM V6.0 Clean Algorithm initialized:")
        print(f"   Formula: (Views/h × {velocity_weight}) + (Engagement×Views × {engagement_weight}) + (Views×Decay × {freshness_weight})")
        print(f"   Trending Page Bonus: +{(trending_page_bonus-1)*100:.0f}%")
        print(f"   Time Decay: {time_decay_hours}h")
    
    def calculate_score(self, video: VideoData, regional_boost: float = 0.0) -> TrendingResult:
        """
        V6.0 MOMENTUM Score Calculation
        
        Args:
            video: Video data
            regional_boost: Additional regional relevance boost (0.0-1.0)
            
        Returns:
            TrendingResult with detailed breakdown
        """
        
        # Basis-Metriken
        views = max(video.views, 1)
        comments = video.comments
        likes = video.likes
        age_hours = max(video.age_hours, 0.1)
        
        # 1. VELOCITY: Views pro Stunde (60% Gewichtung)
        views_per_hour = views / age_hours
        velocity_score = views_per_hour * self.velocity_weight
        
        # 2. ENGAGEMENT: Engagement-Rate × Views (30% Gewichtung)
        engagement_rate = (likes + comments) / views
        engagement_score = engagement_rate * views * self.engagement_weight
        
        # 3. FRESHNESS: Views × Zeit-Dämpfung (10% Gewichtung)
        time_decay = math.exp(-age_hours / self.time_decay_hours)
        freshness_score = views * time_decay * self.freshness_weight
        
        # BASE MOMENTUM SCORE
        base_momentum_score = velocity_score + engagement_score + freshness_score
        
        # V6.0 ENHANCEMENTS
        final_score = base_momentum_score
        
        # Apply Trending Page Bonus
        if video.is_trending_page_video:
            final_score *= self.trending_page_bonus
        
        # Apply Regional Boost  
        if regional_boost > 0:
            regional_multiplier = 1.0 + (regional_boost * 0.2)  # Max +20%
            final_score *= regional_multiplier
        
        # Create detailed breakdown
        breakdown = {
            'velocity_score': velocity_score,
            'engagement_score': engagement_score,
            'freshness_score': freshness_score,
            'base_score': base_momentum_score,
            'trending_bonus_applied': video.is_trending_page_video,
            'regional_boost_applied': regional_boost > 0,
            'final_score': final_score
        }
        
        # Debug für interessante Videos
        if age_hours < 6 or video.is_trending_page_video:
            print(f"🔍 MOMENTUM V6.0: {video.title[:40]}...")
            print(f"   Views: {views:,}, Age: {age_hours:.1f}h, Source: {video.source}")
            print(f"   Velocity: {views_per_hour:,.0f}/h → {velocity_score:,.0f}")
            print(f"   Engagement: {engagement_rate:.4f} × {views:,} → {engagement_score:,.0f}")
            print(f"   Freshness: {time_decay:.3f} → {freshness_score:,.0f}")
            print(f"   Base MOMENTUM: {base_momentum_score:,.0f}")
            if video.is_trending_page_video:
                print(f"   🔥 Trending Bonus: +{(self.trending_page_bonus-1)*100:.0f}%")
            if regional_boost > 0:
                print(f"   🎯 Regional Boost: +{regional_boost*20:.0f}%")
            print(f"   🚀 FINAL SCORE: {final_score:,.0f}")
        
        return TrendingResult(
            video_data=video,
            trending_score=final_score,
            rank=0,  # Set later during ranking
            normalized_score=0.0,  # Calculated later
            confidence=self._calculate_confidence(video, final_score),
            is_truly_trending=video.is_trending_page_video,
            regional_relevance_score=regional_boost,
            momentum_breakdown=breakdown
        )
    
    def _calculate_confidence(self, video: VideoData, score: float) -> float:
        """
        Calculate confidence score based on video metrics
        Higher confidence for:
        - Videos from trending pages
        - Videos with balanced engagement
        - Videos with sufficient data
        """
        confidence = 0.5  # Base confidence
        
        # Trending page videos get higher confidence
        if video.is_trending_page_video:
            confidence += 0.3
        
        # Balanced engagement ratio increases confidence
        if video.views > 0:
            engagement_ratio = (video.likes + video.comments) / video.views
            if 0.001 <= engagement_ratio <= 0.1:  # Reasonable engagement
                confidence += 0.2
        
        # Sufficient views increase confidence
        if video.views >= 1000:
            confidence += 0.1
        
        # Age factor (not too old, not too new)
        if 1 <= video.age_hours <= 72:  # 1h to 3 days
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """V6.0 Algorithm Information for API"""
        return {
            "version": self.version,
            "name": "MOMENTUM V6.0 Clean Algorithm",
            "description": "Velocity-focused trending detection with regional boost",
            "formula": f"(Views/h × {self.velocity_weight}) + (Engagement×Views × {self.engagement_weight}) + (Views×Decay × {self.freshness_weight})",
            "components": {
                "velocity": {
                    "weight": self.velocity_weight,
                    "description": "Views per hour - primary trend indicator"
                },
                "engagement": {
                    "weight": self.engagement_weight, 
                    "description": "Engagement rate × total views"
                },
                "freshness": {
                    "weight": self.freshness_weight,
                    "description": "Time decay favoring newer content"
                }
            },
            "v6_enhancements": {
                "trending_page_bonus": f"+{(self.trending_page_bonus-1)*100:.0f}%",
                "regional_boost": "Up to +20% for regional relevance",
                "confidence_scoring": "Multi-factor confidence calculation",
                "source_tracking": "Trending page vs API source identification"
            },
            "parameters": {
                "velocity_weight": self.velocity_weight,
                "engagement_weight": self.engagement_weight,
                "freshness_weight": self.freshness_weight,
                "time_decay_hours": self.time_decay_hours,
                "trending_page_bonus": self.trending_page_bonus
            }
        }


def create_momentum_algorithm(config: Optional[Dict[str, Any]] = None) -> MomentumAlgorithm:
    """Factory function for MOMENTUM Algorithm with optional config"""
    if config:
        return MomentumAlgorithm(**config)
    else:
        return MomentumAlgorithm()  # Use defaults


# Quick Test Function
if __name__ == "__main__":
    # Test MOMENTUM Algorithm
    algorithm = MomentumAlgorithm()
    
    # Test video from trending page
    trending_video = VideoData(
        video_id="test1",
        title="Viral Gaming Video",
        channel="TopGamer",
        views=100000,
        comments=2000,
        likes=8000, 
        duration_seconds=600,
        age_hours=2.0,
        published_at="2024-01-01T12:00:00Z",
        is_trending_page_video=True,
        source="trending_page"
    )
    
    # Test video from API
    api_video = VideoData(
        video_id="test2", 
        title="Regular Gaming Video",
        channel="RegularGamer",
        views=50000,
        comments=800,
        likes=3000,
        duration_seconds=720,
        age_hours=12.0,
        published_at="2024-01-01T02:00:00Z",
        is_trending_page_video=False,
        source="api"
    )
    
    print("\n🧪 MOMENTUM V6.0 Algorithm Test")
    print("=" * 50)
    
    result1 = algorithm.calculate_score(trending_video, regional_boost=0.3)
    result2 = algorithm.calculate_score(api_video, regional_boost=0.1)
    
    print(f"\nRanking:")
    results = [result1, result2]
    results.sort(key=lambda x: x.trending_score, reverse=True)
    
    for i, result in enumerate(results, 1):
        print(f"#{i}: {result.video_data.title} - Score: {result.trending_score:.0f} - Source: {result.video_data.source}")
