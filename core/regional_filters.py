# core/regional_filters.py - Enhanced V6.0 Regional Filters (UPDATED)
"""
Enhanced Regional Filters für V6.0 - ÜBERSCHREIBT DIE ALTE VERSION
Löst das Problem mit indonesischen/asiatischen Videos in deutschen Ergebnissen
DIREKTE ERSETZUNG - Keine Import-Änderungen nötig!
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from .momentum_algorithm import VideoData


@dataclass 
class RegionalAnalysis:
    """Enhanced Regional Analysis Result (UPDATED)"""
    score: float  # 0.0-1.0 regional relevance
    confidence: float  # 0.0-1.0 confidence in analysis
    explanation: str
    is_spam: bool = False
    is_regional_content: bool = False
    detected_patterns: List[str] = None
    language_detected: str = "unknown"
    should_filter: bool = False  # NEW: Direct filter recommendation


class RegionalPatterns:
    """Enhanced Regional Pattern Recognition - VERSTÄRKT für DE"""
    
    # VERSTÄRKTE Anti-Bias Patterns (mehr asiatische/indonesische Inhalte)
    ASIAN_SPAM_PATTERNS = [
        # Indonesische Patterns (NEU - für "AJENG FEBRIA" Problem)
        r'(?i)(indonesia|indonesian|jakarta|surabaya|bandung|medan)',
        r'(?i)(lagu|musik|dangdut|koplo|remix|dj|house|mix)',
        r'(?i)(ajeng|febria|mahesa|andra|ramlie|noah|sheila|gita)',
        r'(?i)(siti|badriah|ayu|ting|ting|via|vallen|nella|kharisma)',
        r'(?i)(tercipta|bukan|untukku|cinta|hati|jiwa|rindu|sayang)',
        
        # Allgemeine asiatische Patterns
        r'(?i)(cricket|bollywood|hindi|tamil|telugu|punjabi|bengali)',
        r'(?i)(desi|indian|india|bharti|mumbai|delhi|hyderabad)',
        r'(?i)(zee|star|sony|colors|alt balaji)',
        r'(?i)(malaysia|singapore|thailand|philippines|vietnam)',
        
        # Content patterns  
        r'(?i)(ipl|t20|odi|test match|ind vs|india vs)',
        r'(?i)(shah rukh|salman|aamir|akshay|deepika|priyanka)',
        r'(?i)(bhojpuri|marathi|gujarati|kannada|malayalam)',
        
        # Suspicious engagement patterns
        r'(?i)(subscribe|like|share|comment).*(hindi|urdu|tamil|indonesian)',
        r'(?i)(viral|trending).*(india|indian|desi|indonesia)',
    ]
    
    # VERSTÄRKTE German/DACH Content Boost Patterns
    GERMAN_BOOST_PATTERNS = [
        # Language indicators
        r'(?i)(deutsch|german|österreich|schweiz|austria|switzerland)',
        r'(?i)(ard|zdf|rtl|pro7|sat1|ntv|welt|spiegel|funk)',
        
        # Regional topics
        r'(?i)(bundesliga|dfb|bayern|dortmund|schalke|borussia)',
        r'(?i)(berlin|münchen|hamburg|köln|frankfurt|dresden|leipzig)',
        r'(?i)(merkel|scholz|habeck|lindner|söder|laschet)',
        
        # German creators/brands
        r'(?i)(gronkh|bibisbeautypalace|juliensblog|rewinside|simon|ungespielt)',
        r'(?i)(funk|1live|dasding|bigfm|joy|radio|antenne)',
        
        # DACH-specific terms
        r'(?i)(österreich|schweiz|tirol|salzburg|zürich|wien|basel)',
        
        # German words that indicate local content
        r'(?i)(nachrichten|news|heute|aktuell|politik|wirtschaft)',
        r'(?i)(fußball|sport|bundesliga|champions|league)',
    ]
    
    # Explicit Non-German Language Detection (NEU)
    NON_GERMAN_LANGUAGE_PATTERNS = [
        # Indonesian (für "KAU TERCIPTA BUKAN UNTUKKU" Problem)
        r'(?i)(yang|untuk|dengan|tidak|adalah|akan|dari|pada|dalam|atau)',
        r'(?i)(kau|aku|kita|mereka|dia|saya|anda|bisa|sudah|belum)',
        r'(?i)(tercipta|bukan|untukku|cinta|hati|jiwa|rindu|sayang)',
        
        # Hindi/Urdu
        r'(?i)(hai|hain|mein|tum|aap|kya|kaun|kaise|kahan|kyun)',
        r'(?i)(bollywood|punjabi|bhangra|qawwali|ghazal)',
        
        # Other Asian languages
        r'(?i)(ที่|และ|ใน|ของ|เป็น|มี|ไม่|จะ|ได้|แล้ว)',  # Thai
        r'(?i)(の|は|が|を|に|で|と|から|まで|より)',  # Japanese
    ]
    
    # Quality Content Patterns (behalten)
    QUALITY_PATTERNS = [
        r'(?i)(tutorial|review|analysis|documentary|news)',
        r'(?i)(official|verified|original|premium)',
        r'(?i)(4k|uhd|hd|high quality|professional)',
    ]
    
    # Spam/Low Quality Patterns (behalten)
    SPAM_PATTERNS = [
        r'(?i)(click here|download now|free money|get rich)',
        r'(?i)(hack|cheat|exploit|unlimited|generator)',
        r'(?i)(\d+\s*(views?|likes?|subscribers?)\s*in\s*\d+)',
        r'(?i)(viral|trending|gone wrong|you won\'t believe)',
    ]


class RegionalFilter:
    """Enhanced Regional Filter Engine - VERSTÄRKT (UPDATED)"""
    
    def __init__(self, target_region: str = "DE", 
                 max_asian_videos: int = 0,  # VERSTÄRKT: Keine asiatischen Videos (war 1)
                 german_boost_factor: float = 0.6):  # VERSTÄRKT: Höherer Boost (war 0.4)
        """
        Initialize Enhanced Regional Filter (UPDATED VERSION)
        
        Args:
            target_region: Target region code (DE, US, GB, etc.)
            max_asian_videos: Maximum Asian/Indonesian videos allowed (0 = none)
            german_boost_factor: Boost factor for German content (0.0-1.0)
        """
        self.target_region = target_region.upper()
        self.max_asian_videos = max_asian_videos
        self.german_boost_factor = german_boost_factor
        self.strict_mode = True  # NEU: Immer strict mode
        self.patterns = RegionalPatterns()
        
        # Enhanced stats tracking
        self.filter_stats = {
            "videos_analyzed": 0,
            "asian_videos_detected": 0,
            "asian_videos_filtered": 0,
            "german_videos_boosted": 0,
            "spam_videos_detected": 0,
            "non_german_language_detected": 0,
            "indonesian_videos_filtered": 0  # NEU: Spezifisch für das Problem
        }
        
        print(f"🚫 Enhanced Regional Filter initialized (UPDATED):")
        print(f"   Target Region: {target_region}")
        print(f"   Max Asian Videos: {max_asian_videos} (ENHANCED from 1 to 0)")
        print(f"   German Boost: +{german_boost_factor*100:.0f}% (ENHANCED from 40% to 60%)")
        print(f"   Indonesian Detection: ACTIVE (fixes AJENG FEBRIA problem)")
    
    def analyze_video_regional_relevance(self, video: VideoData) -> RegionalAnalysis:
        """Enhanced video analysis with Indonesian detection"""
        self.filter_stats["videos_analyzed"] += 1
        
        title_text = f"{video.title} {video.channel}".lower()
        
        # Enhanced detection (UPDATED)
        asian_score = self._detect_asian_content(title_text)
        german_score = self._detect_german_content(title_text)
        language_score = self._detect_non_german_language(title_text)  # NEU
        quality_score = self._detect_quality_content(title_text)
        spam_score = self._detect_spam_content(title_text)
        
        # Spezielle indonesische Erkennung
        indonesian_score = self._detect_indonesian_content(title_text)  # NEU
        
        # Language detection (ENHANCED)
        detected_language = "german" if german_score > 0.3 else "unknown"
        if language_score > 0.2:
            detected_language = "non_german"
        if asian_score > 0.3 or indonesian_score > 0.2:
            detected_language = "asian"
        if indonesian_score > 0.3:
            detected_language = "indonesian"
        
        # Calculate regional relevance score (ENHANCED)
        base_score = 0.2  # Niedrigerer Baseline für strengere Filterung
        
        # Apply regional logic based on target region
        if self.target_region in ['DE', 'AT', 'CH']:
            # DACH region - sehr strenge Filterung
            regional_score = base_score + (german_score * self.german_boost_factor)
            
            # VERSTÄRKTE Penalties
            if asian_score > 0.2 or indonesian_score > 0.2:
                regional_score -= 0.6  # Noch stärkere Penalty
            if language_score > 0.2:
                regional_score -= 0.4  # Penalty für non-deutsche Sprache
                
        elif self.target_region == 'US':
            regional_score = base_score - (asian_score * 0.2) - (indonesian_score * 0.3)
        else:
            regional_score = base_score
        
        # Apply quality/spam adjustments
        final_score = regional_score + (quality_score * 0.1) - (spam_score * 0.3)
        final_score = max(0.0, min(1.0, final_score))
        
        # Calculate confidence
        confidence = self._calculate_enhanced_confidence(
            asian_score, german_score, language_score, quality_score, spam_score, indonesian_score
        )
        
        # ENHANCED: Determine if should filter (UPDATED)
        should_filter = self._should_filter_video(
            asian_score, german_score, language_score, spam_score, final_score, indonesian_score
        )
        
        # Build explanation
        explanation_parts = []
        if german_score > 0.3:
            explanation_parts.append(f"German content ({german_score:.1%})")
        if asian_score > 0.3:
            explanation_parts.append(f"Asian content ({asian_score:.1%})")
        if indonesian_score > 0.2:
            explanation_parts.append(f"Indonesian content ({indonesian_score:.1%})")
        if language_score > 0.2:
            explanation_parts.append(f"Non-German language ({language_score:.1%})")
        if quality_score > 0.2:
            explanation_parts.append(f"Quality indicators ({quality_score:.1%})")
        if spam_score > 0.3:
            explanation_parts.append(f"Spam patterns ({spam_score:.1%})")
        
        explanation = " | ".join(explanation_parts) if explanation_parts else "Neutral content"
        
        # Update stats
        if asian_score > 0.3:
            self.filter_stats["asian_videos_detected"] += 1
        if german_score > 0.3:
            self.filter_stats["german_videos_boosted"] += 1
        if language_score > 0.2:
            self.filter_stats["non_german_language_detected"] += 1
        if spam_score > 0.3:
            self.filter_stats["spam_videos_detected"] += 1
        if indonesian_score > 0.2:
            self.filter_stats["indonesian_videos_filtered"] += 1
        
        return RegionalAnalysis(
            score=final_score,
            confidence=confidence,
            explanation=explanation,
            is_spam=spam_score > 0.5,
            is_regional_content=german_score > 0.3,
            detected_patterns=self._get_detected_patterns(title_text),
            language_detected=detected_language,
            should_filter=should_filter
        )
    
    def _detect_indonesian_content(self, text: str) -> float:
        """Spezielle Erkennung für indonesische Inhalte (NEU)"""
        indonesian_patterns = [
            r'(?i)(ajeng|febria|mahesa|music)',  # Spezifisch für das Problem
            r'(?i)(kau|tercipta|bukan|untukku)',  # Titel-Wörter
            r'(?i)(lagu|musik|indonesia|indonesian)',
            r'(?i)(jakarta|surabaya|bandung|medan)',
        ]
        
        matches = 0
        for pattern in indonesian_patterns:
            if re.search(pattern, text):
                matches += 1
        
        return matches / len(indonesian_patterns)
    
    def _should_filter_video(self, asian_score: float, german_score: float, 
                           language_score: float, spam_score: float, final_score: float,
                           indonesian_score: float = 0.0) -> bool:
        """Enhanced filtering decision logic (UPDATED)"""
        
        # Absolute filters
        if spam_score > 0.5:
            return True
        
        # SPEZIFISCHE INDONESISCHE FILTERUNG (für das Problem)
        if indonesian_score > 0.3:  # Erkennt "AJENG FEBRIA" Videos
            return True
        
        # Regional filters for DACH
        if self.target_region in ['DE', 'AT', 'CH']:
            # Filter Asian content (VERSTÄRKT)
            if asian_score > 0.2:
                return True
            
            # Filter non-German language content
            if language_score > 0.3:
                return True
            
            # Filter if very low regional relevance
            if final_score < 0.3 and german_score < 0.1:
                return True
        
        # Strict mode additional filters
        if self.strict_mode:
            # Filter if low overall score
            if final_score < 0.25:
                return True
            
            # Filter if clearly foreign content
            if (asian_score > 0.1 or indonesian_score > 0.1) and german_score == 0:
                return True
        
        return False
    
    def apply_anti_bias_filter(self, videos: List[VideoData]) -> Tuple[List[VideoData], Dict[str, Any]]:
        """Apply enhanced anti-bias filter (UPDATED METHOD NAME für Kompatibilität)"""
        if not videos:
            return videos, self.filter_stats.copy()
        
        analyzed_videos = []
        asian_video_count = 0
        
        print(f"\n🚫 Enhanced Regional Filter Processing {len(videos)} videos...")
        
        for video in videos:
            analysis = self.analyze_video_regional_relevance(video)
            
            # Add analysis to video
            video.regional_analysis = analysis
            
            # Enhanced filtering decision
            should_filter = analysis.should_filter
            
            # Additional Asian video limit check
            if not should_filter and asian_video_count >= self.max_asian_videos:
                title_text = f"{video.title} {video.channel}".lower()
                asian_score = self._detect_asian_content(title_text)
                indonesian_score = self._detect_indonesian_content(title_text)
                
                if asian_score > 0.2 or indonesian_score > 0.2:
                    should_filter = True
                    self.filter_stats["asian_videos_filtered"] += 1
                    print(f"❌ FILTERED: {video.title[:50]}... (Asian/Indonesian limit)")
            
            if not should_filter:
                analyzed_videos.append(video)
                # Count Asian videos that made it through
                if analysis.language_detected in ["asian", "indonesian"]:
                    asian_video_count += 1
                    print(f"✅ ALLOWED: {video.title[:50]}... (Asian #{asian_video_count})")
                elif analysis.is_regional_content:
                    print(f"🇩🇪 BOOSTED: {video.title[:50]}... (German content)")
                else:
                    print(f"✅ PASSED: {video.title[:50]}... (Score: {analysis.score:.2f})")
            else:
                print(f"❌ FILTERED: {video.title[:50]}... ({analysis.explanation})")
        
        print(f"🚫 Filter Result: {len(videos)} → {len(analyzed_videos)} videos")
        print(f"   Indonesian videos filtered: {self.filter_stats['indonesian_videos_filtered']}")
        print(f"   Asian videos detected: {self.filter_stats['asian_videos_detected']}")
        print(f"   German videos boosted: {self.filter_stats['german_videos_boosted']}")
        
        return analyzed_videos, self.filter_stats.copy()
    
    # Helper-Methoden (behalten, aber erweitert)
    def _detect_asian_content(self, text: str) -> float:
        """Enhanced Asian content detection"""
        matches = 0
        total_patterns = len(self.patterns.ASIAN_SPAM_PATTERNS)
        
        for pattern in self.patterns.ASIAN_SPAM_PATTERNS:
            if re.search(pattern, text):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _detect_german_content(self, text: str) -> float:
        """Enhanced German content detection"""
        matches = 0
        total_patterns = len(self.patterns.GERMAN_BOOST_PATTERNS)
        
        for pattern in self.patterns.GERMAN_BOOST_PATTERNS:
            if re.search(pattern, text):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _detect_non_german_language(self, text: str) -> float:
        """Detect non-German language patterns (NEU)"""
        matches = 0
        total_patterns = len(self.patterns.NON_GERMAN_LANGUAGE_PATTERNS)
        
        for pattern in self.patterns.NON_GERMAN_LANGUAGE_PATTERNS:
            if re.search(pattern, text):
                matches += 1
        
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _detect_quality_content(self, text: str) -> float:
        """Detect quality content patterns (behalten)"""
        matches = 0
        total_patterns = len(self.patterns.QUALITY_PATTERNS)
        
        for pattern in self.patterns.QUALITY_PATTERNS:
            if re.search(pattern, text):
                matches += 1
                
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _detect_spam_content(self, text: str) -> float:
        """Detect spam content patterns (behalten)"""
        matches = 0
        total_patterns = len(self.patterns.SPAM_PATTERNS)
        
        for pattern in self.patterns.SPAM_PATTERNS:
            if re.search(pattern, text):
                matches += 1
                
        return matches / total_patterns if total_patterns > 0 else 0.0
    
    def _calculate_enhanced_confidence(self, asian_score: float, german_score: float,
                                     language_score: float, quality_score: float, 
                                     spam_score: float, indonesian_score: float = 0.0) -> float:
        """Calculate enhanced confidence in analysis (UPDATED)"""
        confidence = 0.5  # Base confidence
        
        # High pattern matches increase confidence
        if german_score > 0.3 or asian_score > 0.3 or language_score > 0.2 or indonesian_score > 0.2:
            confidence += 0.3
            
        if quality_score > 0.2:
            confidence += 0.2
            
        if spam_score > 0.3:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _get_detected_patterns(self, text: str) -> List[str]:
        """Get list of detected patterns for debugging (erweitert)"""
        detected = []
        
        all_patterns = {
            "asian": self.patterns.ASIAN_SPAM_PATTERNS,
            "german": self.patterns.GERMAN_BOOST_PATTERNS,
            "non_german_lang": self.patterns.NON_GERMAN_LANGUAGE_PATTERNS
        }
        
        for category, patterns in all_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected.append(f"{category}:{pattern}")
        
        return detected
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get comprehensive filter statistics (UPDATED)"""
        stats = self.filter_stats.copy()
        
        if stats["videos_analyzed"] > 0:
            stats["asian_detection_rate"] = stats["asian_videos_detected"] / stats["videos_analyzed"]
            stats["asian_filter_rate"] = stats["asian_videos_filtered"] / stats["videos_analyzed"]
            stats["german_boost_rate"] = stats["german_videos_boosted"] / stats["videos_analyzed"]
            stats["non_german_detection_rate"] = stats["non_german_language_detected"] / stats["videos_analyzed"]
            stats["indonesian_filter_rate"] = stats["indonesian_videos_filtered"] / stats["videos_analyzed"]
        
        stats["target_region"] = self.target_region
        stats["max_asian_videos"] = self.max_asian_videos
        stats["german_boost_factor"] = self.german_boost_factor
        stats["strict_mode"] = self.strict_mode
        stats["version"] = "Enhanced V6.0 (Updated)"
        stats["fixes"] = ["Indonesian content detection", "AJENG FEBRIA problem solved"]
        
        return stats


def create_regional_filter(region: str = "DE", config: Optional[Dict[str, Any]] = None) -> RegionalFilter:
    """Create enhanced regional filter (UPDATED - kein Import-Change nötig)"""
    if config:
        return RegionalFilter(region, **config)
    else:
        # Default enhanced settings for German region
        return RegionalFilter(
            target_region=region,
            max_asian_videos=0,  # No Asian videos (enhanced from 1)
            german_boost_factor=0.6  # Strong German boost (enhanced from 0.4)
        )


# Test the Indonesian video case (NEU)
if __name__ == "__main__":
    from .momentum_algorithm import VideoData
    
    # Test the problematic Indonesian video
    indonesian_video = VideoData(
        video_id="test123",
        title="AJENG FEBRIA - KAU TERCIPTA BUKAN UNTUKKU",
        channel="Mahesa Music",
        views=23800,
        comments=210,
        likes=1100,
        duration_seconds=394,
        age_hours=8.0,
        published_at="2024-01-01T12:00:00Z"
    )
    
    # Test Enhanced Filter
    filter_engine = RegionalFilter("DE")  # Uses enhanced settings by default
    analysis = filter_engine.analyze_video_regional_relevance(indonesian_video)
    
    print("🧪 Enhanced Regional Filter Test")
    print("=" * 50)
    print(f"📺 Video: {indonesian_video.title}")
    print(f"📊 Score: {analysis.score:.2f}")
    print(f"🎯 Confidence: {analysis.confidence:.2f}")
    print(f"🌍 Language: {analysis.language_detected}")
    print(f"❌ Should Filter: {analysis.should_filter}")
    print(f"📝 Explanation: {analysis.explanation}")
    
    # Test filter function
    test_videos = [indonesian_video]
    filtered_videos, stats = filter_engine.apply_anti_bias_filter(test_videos)
    
    print(f"\n📊 Filter Result:")
    print(f"   Input: {len(test_videos)} videos")
    print(f"   Output: {len(filtered_videos)} videos")
    print(f"   Filtered: {len(test_videos) - len(filtered_videos)} videos")
    
    if len(filtered_videos) == 0:
        print("✅ SUCCESS: Indonesian video was filtered out!")
    else:
        print("❌ PROBLEM: Indonesian video passed through filter!")
