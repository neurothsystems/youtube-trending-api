# core/regional_filters.py - V6.0 Regional & Anti-Bias Filters
"""
V6.0 Regional Filters & Anti-Bias Logic
Modulares System für schnelle Anpassungen von Regional-Logic
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from .momentum_algorithm import VideoData


@dataclass 
class RegionalAnalysis:
    """Regional Analysis Result"""
    score: float  # 0.0-1.0 regional relevance
    confidence: float  # 0.0-1.0 confidence in analysis
    explanation: str
    is_spam: bool = False
    is_regional_content: bool = False
    detected_patterns: List[str] = None
    

class RegionalPatterns:
    """V6.0 Regional Pattern Recognition"""
    
    # Anti-Bias Patterns (suspiciously Asian/Indian content)
    ASIAN_SPAM_PATTERNS = [
        # Channel patterns
        r'(?i)(cricket|bollywood|hindi|tamil|telugu|punjabi|bengali)',
        r'(?i)(desi|indian|india|bharti|mumbai|delhi|hyderabad)',
        r'(?i)(zee|star|sony|colors|alt balaji)',
        
        # Content patterns  
        r'(?i)(ipl|t20|odi|test match|ind vs|india vs)',
        r'(?i)(shah rukh|salman|aamir|akshay|deepika|priyanka)',
        r'(?i)(bhojpuri|marathi|gujarati|kannada|malayalam)',
        
        # Suspicious engagement patterns
        r'(?i)(subscribe|like|share|comment).*(hindi|urdu|tamil)',
        r'(?i)(viral|trending).*(india|indian|desi)',
    ]
    
    # German/DACH Content Boost Patterns
    GERMAN_BOOST_PATTERNS = [
        # Language indicators
        r'(?i)(deutsch|german|österreich|schweiz|austria|switzerland)',
        r'(?i)(ard|zdf|rtl|pro7|sat1|ntv|welt|spiegel)',
        
        # Regional topics
        r'(?i)(bundesliga|dfb|bayern|dortmund|schalke)',
        r'(?i)(berlin|münchen|hamburg|köln|frankfurt|dresden)',
        r'(?i)(merkel|scholz|habeck|lindner|söder)',
        
        # German creators/brands
        r'(?i)(gronkh|bibisbeautypalace|juliensblog|rewinside)',
        r'(?i)(funk|1live|dasding|bigfm)',
        
        # DACH-specific terms
        r'(?i)(österreich|schweiz|tirol|salzburg|zürich|wien)',
    ]
    
    # Quality Content Patterns (boost confidence)
    QUALITY_PATTERNS = [
        r'(?i)(tutorial|review|analysis|documentary|news)',
        r'(?i)(official|verified|original|premium)',
        r'(?i)(4k|uhd|hd|high quality|professional)',
    ]
    
    # Spam/Low Quality Patterns (reduce confidence) 
    SPAM_PATTERNS = [
        r'(?i)(click here|download now|free money|get rich)',
        r'(?i)(hack|cheat|exploit|unlimited|generator)',
        r'(?i)(\d+\s*(views?|likes?|subscribers?)\s*in\s*\d+)',
        r'(?i)(viral|trending|gone wrong|you won\'t believe)',
    ]


class RegionalFilter:
    """V6.0 Regional Filter Engine"""
    
    def __init__(self, target_region: str = "DE", 
                 max_asian_videos: int = 1,
                 german_boost_factor: float = 0.4):
        """
        Initialize Regional Filter
        
        Args:
            target_region: Target region code (DE, US, GB, etc.)
            max_asian_videos: Maximum Asian/Indian videos allowed
            german_boost_factor: Boost factor for German content (0.0-1.0)
        """
        self.target_region = target_region.upper()
        self.max_asian_videos = max_asian_videos
        self.german_boost_factor = german_boost_factor
        self.patterns = RegionalPatterns()
        
        # Stats tracking
        self.filter_stats = {
            "videos_analyzed": 0,
            "asian_videos_detected": 0,
            "asian_videos_filtered": 0,
            "german_videos_boosted": 0,
            "spam_videos_detected": 0
        }
    
    def analyze_video_regional_relevance(self, video: VideoData) -> RegionalAnalysis:
        """
        Analyze video for regional relevance and spam detection
        
        Returns:
            RegionalAnalysis with score, confidence, and explanations
        """
        self.filter_stats["videos_analyzed"] += 1
        
        title_text = f"{video.title} {video.channel}".lower()
        
        # Check for Asian/Indian content
        asian_score = self._detect_asian_content(title_text)
        
        # Check for German/DACH content
        german_score = self._detect_german_content(title_text)
        
        # Check for quality indicators
        quality_score = self._detect_quality_content(title_text)
        
        # Check for spam
        spam_score = self._detect_spam_content(title_text)
        
        # Calculate final regional relevance score
        base_score = 0.3  # Neutral baseline
        
        # Apply regional boosts/penalties
        if self.target_region in ['DE', 'AT', 'CH']:
            # DACH region - boost German content, penalize Asian
            regional_score = base_score + (german_score * self.german_boost_factor) - (asian_score * 0.3)
        elif self.target_region == 'US':
            # US region - neutral to Asian, slight boost to English
            regional_score = base_score - (asian_score * 0.1)
        else:
            # Other regions - use base score
            regional_score = base_score
        
        # Apply quality/spam adjustments
        final_score = regional_score + (quality_score * 0.2) - (spam_score * 0.3)
        final_score = max(0.0, min(1.0, final_score))  # Clamp to 0-1
        
        # Calculate confidence
        confidence = self._calculate_confidence(asian_score, german_score, quality_score, spam_score)
        
        # Determine if spam
        is_spam = spam_score > 0.5 or (asian_score > 0.7 and self.target_region in ['DE', 'AT', 'CH'])
        
        # Build explanation
        explanation = self._build_explanation(asian_score, german_score, quality_score, spam_score, final_score)
        
        # Update stats
        if asian_score > 0.5:
            self.filter_stats["asian_videos_detected"] += 1
        if german_score > 0.5:
            self.filter_stats["german_videos_boosted"] += 1
        if spam_score > 0.3:
            self.filter_stats["spam_videos_detected"] += 1
        
        return RegionalAnalysis(
            score=final_score,
            confidence=confidence,
            explanation=explanation,
            is_spam=is_spam,
            is_regional_content=german_score > 0.3,
            detected_patterns=self._get_detected_patterns(title_text)
        )
    
    def apply_anti_bias_filter(self, videos: List[VideoData]) -> Tuple[List[VideoData], Dict[str, Any]]:
        """
        Apply anti-bias filter to video list
        Limits Asian content based on max_asian_videos setting
        """
        if not videos:
            return videos, self.filter_stats.copy()
        
        analyzed_videos = []
        asian_video_count = 0
        
        for video in videos:
            analysis = self.analyze_video_regional_relevance(video)
            
            # Add analysis to video (for later use)
            video.regional_analysis = analysis
            
            # Check if we should filter this video
            should_filter = False
            
            if analysis.is_spam:
                should_filter = True
                
            elif analysis.score < 0.2:  # Very low regional relevance
                should_filter = True
                
            elif asian_video_count >= self.max_asian_videos:
                # Check if this is Asian content
                title_text = f"{video.title} {video.channel}".lower()
                asian_score = self._detect_asian_content(title_text)
                if asian_score > 0.5:
                    should_filter = True
                    self.filter_stats["asian_videos_filtered"] += 1
            
            if not should_filter:
                analyzed_videos.append(video)
                # Count Asian videos that made it through
                title_text = f"{video.title} {video.channel}".lower()
                if self._detect_asian_content(title_text) > 0.5:
                    asian_video_count += 1
        
        return analyzed_videos, self.filter_stats.copy()
    
    def _detect_asian_content(self, text: str) -> float:
        """Detect Asian/Indian content patterns (0.0-1.0)"""
        matches = 0
        total_patterns = len(self.patterns.ASIAN_SPAM_PATTERNS)
        
        for pattern in self.patterns.ASIAN_SPAM_PATTERNS:
            if re.search(pattern, text):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _detect_german_content(self, text: str) -> float:
        """Detect German/DACH content patterns (0.0-1.0)"""
        matches = 0
        total_patterns = len(self.patterns.GERMAN_BOOST_PATTERNS)
        
        for pattern in self.patterns.GERMAN_BOOST_PATTERNS:
            if re.search(pattern, text):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _detect_quality_content(self, text: str) -> float:
        """Detect quality content patterns (0.0-1.0)"""
        matches = 0
        total_patterns = len(self.patterns.QUALITY_PATTERNS)
        
        for pattern in self.patterns.QUALITY_PATTERNS:
            if re.search(pattern, text):
                matches += 1
                
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _detect_spam_content(self, text: str) -> float:
        """Detect spam content patterns (0.0-1.0)"""
        matches = 0
        total_patterns = len(self.patterns.SPAM_PATTERNS)
        
        for pattern in self.patterns.SPAM_PATTERNS:
            if re.search(pattern, text):
                matches += 1
                
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _calculate_confidence(self, asian_score: float, german_score: float, 
                            quality_score: float, spam_score: float) -> float:
        """Calculate confidence in regional analysis"""
        confidence = 0.5  # Base confidence
        
        # High pattern matches increase confidence
        if german_score > 0.3 or asian_score > 0.3:
            confidence += 0.3
            
        if quality_score > 0.2:
            confidence += 0.2
            
        if spam_score > 0.3:
            confidence += 0.2  # High confidence in spam detection
        
        return min(confidence, 1.0)
    
    def _build_explanation(self, asian_score: float, german_score: float,
                          quality_score: float, spam_score: float, final_score: float) -> str:
        """Build human-readable explanation"""
        explanations = []
        
        if german_score > 0.3:
            explanations.append(f"German content detected ({german_score:.1%})")
        if asian_score > 0.3:
            explanations.append(f"Asian content detected ({asian_score:.1%})")
        if quality_score > 0.2:
            explanations.append(f"Quality indicators found ({quality_score:.1%})")
        if spam_score > 0.3:
            explanations.append(f"Spam patterns detected ({spam_score:.1%})")
        
        if not explanations:
            explanations.append("Neutral content")
            
        return " | ".join(explanations)
    
    def _get_detected_patterns(self, text: str) -> List[str]:
        """Get list of detected patterns for debugging"""
        detected = []
        
        all_patterns = {
            "asian": self.patterns.ASIAN_SPAM_PATTERNS,
            "german": self.patterns.GERMAN_BOOST_PATTERNS, 
            "quality": self.patterns.QUALITY_PATTERNS,
            "spam": self.patterns.SPAM_PATTERNS
        }
        
        for category, patterns in all_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected.append(f"{category}:{pattern}")
        
        return detected
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get comprehensive filter statistics"""
        stats = self.filter_stats.copy()
        
        if stats["videos_analyzed"] > 0:
            stats["asian_detection_rate"] = stats["asian_videos_detected"] / stats["videos_analyzed"]
            stats["german_boost_rate"] = stats["german_videos_boosted"] / stats["videos_analyzed"]  
            stats["spam_detection_rate"] = stats["spam_videos_detected"] / stats["videos_analyzed"]
        
        stats["target_region"] = self.target_region
        stats["max_asian_videos"] = self.max_asian_videos
        stats["german_boost_factor"] = self.german_boost_factor
        
        return stats


def create_regional_filter(region: str = "DE", config: Optional[Dict[str, Any]] = None) -> RegionalFilter:
    """Factory function for Regional Filter"""
    if config:
        return RegionalFilter(region, **config)
    else:
        return RegionalFilter(region)


# Test Function
if __name__ == "__main__":
    from .momentum_algorithm import VideoData
    
    # Test Regional Filter
    filter_engine = RegionalFilter("DE")
    
    test_videos = [
        VideoData("1", "German Gaming Tutorial Deutsch", "GermanGamer", 10000, 100, 500, 600, 2.0, "2024-01-01T12:00:00Z"),
        VideoData("2", "Cricket Match India vs Pakistan Highlights", "CricketIndia", 50000, 3000, 1000, 900, 1.0, "2024-01-01T13:00:00Z"),
        VideoData("3", "Viral Gaming Video You Won't Believe", "ClickbaitChannel", 5000, 50, 200, 300, 24.0, "2024-01-01T01:00:00Z")
    ]
    
    print("🧪 Regional Filter Test")
    print("=" * 40)
    
    for video in test_videos:
        analysis = filter_engine.analyze_video_regional_relevance(video)
        print(f"\n📺 {video.title[:40]}...")
        print(f"   Score: {analysis.score:.2f} | Confidence: {analysis.confidence:.2f}")
        print(f"   Spam: {analysis.is_spam} | Regional: {analysis.is_regional_content}")
        print(f"   Explanation: {analysis.explanation}")
    
    # Test anti-bias filter
    filtered_videos, stats = filter_engine.apply_anti_bias_filter(test_videos)
    print(f"\n📊 Filter Results: {len(test_videos)} → {len(filtered_videos)} videos")
    print(f"Stats: {stats}")
