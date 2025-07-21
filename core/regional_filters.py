# core/smart_regional_filters.py - Smart Contextual Regional Filter
"""
Smart Contextual Regional Filter für V6.0
Intelligente, kontext-bewusste Filterung statt harte Blacklists
Analysiert Suchintention und passt Filterung entsprechend an
"""

import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
from .momentum_algorithm import VideoData


@dataclass 
class SmartRegionalAnalysis:
    """Smart Regional Analysis Result"""
    score: float  # 0.0-1.0 regional relevance
    confidence: float  # 0.0-1.0 confidence in analysis
    explanation: str
    is_spam: bool = False
    is_regional_content: bool = False
    detected_patterns: List[str] = None
    language_detected: str = "unknown"
    query_intent_match: float = 0.0  # NEW: How well does this match the search intent?
    should_filter: bool = False


@dataclass
class SearchContext:
    """Search Context Analysis"""
    query: str
    target_region: str
    intent_language: str = "neutral"  # detected language intent
    intent_region: str = "neutral"   # detected region intent
    intent_type: str = "general"     # general, specific_region, specific_language
    regional_preference: float = 1.0  # how much to prefer regional content (0.0-2.0)


class SmartPatternDetector:
    """Smart Pattern Detection - Context Aware"""
    
    # Regional Intent Keywords
    REGIONAL_INTENT_PATTERNS = {
        'german': [
            r'(?i)\b(deutsch|german|germany|deutschland)\b',
            r'(?i)\b(österreich|schweiz|austria|switzerland)\b',
            r'(?i)\b(bundesliga|oktoberfest|lederhosen)\b'
        ],
        'asian': [
            r'(?i)\b(asian|asia|japanese|korean|chinese|thai|vietnamese)\b',
            r'(?i)\b(k-pop|jpop|anime|manga|bollywood)\b',
            r'(?i)\b(japan|korea|china|thailand|india|indonesia)\b'
        ],
        'indonesian': [
            r'(?i)\b(indonesian|indonesia|jakarta|bali)\b',
            r'(?i)\b(dangdut|gamelan|batik)\b'
        ],
        'english': [
            r'(?i)\b(english|american|british|us|uk|usa)\b',
            r'(?i)\b(billboard|hollywood|nashville)\b'
        ]
    }
    
    # Quality Indicators (language-neutral)
    QUALITY_INDICATORS = [
        r'(?i)\b(official|hd|4k|premium|verified)\b',
        r'(?i)\b(tutorial|review|documentary|analysis)\b',
        r'(?i)\b(live|concert|performance|festival)\b'
    ]
    
    # Spam Indicators (universal)
    SPAM_INDICATORS = [
        r'(?i)\b(click here|download now|free money)\b',
        r'(?i)\b(hack|cheat|exploit|unlimited coins)\b',
        r'(?i)\d+\s*(views?|subscribers?)\s*in\s*\d+\s*(hours?|days?)',
        r'(?i)\b(gone wrong|you won\'t believe|shocking)\b'
    ]
    
    # Language Detection Patterns
    LANGUAGE_PATTERNS = {
        'german': [
            r'(?i)\b(und|der|die|das|ist|ein|eine|nicht|mit|von|für)\b',
            r'(?i)\b(heute|nachrichten|bundesliga|musik|video)\b'
        ],
        'indonesian': [
            r'(?i)\b(yang|untuk|dengan|tidak|adalah|dari|dan|ini|itu)\b',
            r'(?i)\b(musik|lagu|video|official|live|cover)\b'
        ],
        'english': [
            r'(?i)\b(the|and|for|with|this|that|music|video|official)\b'
        ]
    }


class SmartRegionalFilter:
    """Smart Contextual Regional Filter"""
    
    def __init__(self, target_region: str = "DE"):
        """
        Initialize Smart Regional Filter
        
        Args:
            target_region: Default target region
        """
        self.target_region = target_region.upper()
        self.detector = SmartPatternDetector()
        
        # Smart stats tracking
        self.filter_stats = {
            "videos_analyzed": 0,
            "context_matches": 0,
            "context_mismatches": 0,
            "quality_boosted": 0,
            "spam_filtered": 0,
            "regional_boosted": 0,
            "intent_language_detected": {},
            "intent_region_detected": {}
        }
        
        print(f"🧠 Smart Contextual Regional Filter initialized:")
        print(f"   Target Region: {target_region}")
        print(f"   Mode: Context-aware flexible filtering")
        print(f"   Approach: Intent-based instead of blacklists")
    
    def analyze_search_context(self, query: str, region: str) -> SearchContext:
        """Analyze search context to understand user intent"""
        
        query_lower = query.lower()
        
        # Detect language intent
        intent_language = "neutral"
        for language, patterns in self.detector.REGIONAL_INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    intent_language = language
                    break
            if intent_language != "neutral":
                break
        
        # Detect region intent
        intent_region = region.lower()  # Default to search region
        
        # Detect intent type
        intent_type = "general"
        if intent_language != "neutral":
            intent_type = "specific_language"
        if any(country in query_lower for country in ['japan', 'korea', 'indonesia', 'germany', 'usa']):
            intent_type = "specific_region"
        
        # Calculate regional preference
        regional_preference = 1.0  # Default neutral
        
        if intent_language == "neutral" and intent_type == "general":
            # General search in specific region -> prefer regional content
            regional_preference = 1.5
        elif intent_language != "neutral":
            # Specific language requested -> prefer that language
            regional_preference = 0.8 if intent_language == region.lower() else 0.3
        
        context = SearchContext(
            query=query,
            target_region=region,
            intent_language=intent_language,
            intent_region=intent_region,
            intent_type=intent_type,
            regional_preference=regional_preference
        )
        
        print(f"🧠 Search Context: '{query}' in {region}")
        print(f"   Intent Language: {intent_language}")
        print(f"   Intent Type: {intent_type}")
        print(f"   Regional Preference: {regional_preference:.1f}")
        
        return context
    
    def analyze_video_smart_relevance(self, video: VideoData, context: SearchContext) -> SmartRegionalAnalysis:
        """Smart analysis based on search context"""
        
        self.filter_stats["videos_analyzed"] += 1
        
        title_text = f"{video.title} {video.channel}".lower()
        
        # Detect video characteristics
        video_language = self._detect_video_language(title_text)
        video_quality = self._detect_quality_score(title_text)
        spam_score = self._detect_spam_score(title_text)
        
        # Calculate query-intent match
        intent_match = self._calculate_intent_match(title_text, context)
        
        # Calculate smart regional score
        base_score = 0.5  # Neutral baseline
        
        # Apply context-aware scoring
        if context.intent_type == "general":
            # General search -> prefer regional content
            if video_language == context.target_region.lower() or video_language == "german":
                base_score += 0.3 * context.regional_preference
            elif video_language in ["indonesian", "asian"] and context.target_region == "DE":
                base_score -= 0.2  # Slight penalty for non-regional in general search
        
        elif context.intent_type == "specific_language":
            # Specific language requested -> match intent
            if video_language == context.intent_language:
                base_score += 0.4  # Strong boost for matching intent
                intent_match += 0.3
            elif video_language != context.intent_language:
                base_score -= 0.1  # Small penalty for not matching
        
        elif context.intent_type == "specific_region":
            # Specific region requested -> match that region
            region_match = self._calculate_region_match(title_text, context.intent_region)
            base_score += region_match * 0.4
            intent_match += region_match
        
        # Apply quality/spam adjustments
        final_score = base_score + (video_quality * 0.2) - (spam_score * 0.4)
        final_score = max(0.0, min(1.0, final_score))
        
        # Smart filtering decision
        should_filter = self._smart_filter_decision(
            spam_score, final_score, intent_match, context, video_language
        )
        
        # Build explanation
        explanation = self._build_smart_explanation(
            video_language, video_quality, spam_score, intent_match, context
        )
        
        # Update stats
        self._update_smart_stats(video_language, intent_match, video_quality, spam_score)
        
        return SmartRegionalAnalysis(
            score=final_score,
            confidence=self._calculate_smart_confidence(video_quality, spam_score, intent_match),
            explanation=explanation,
            is_spam=spam_score > 0.6,
            is_regional_content=video_language == context.target_region.lower(),
            detected_patterns=[],
            language_detected=video_language,
            query_intent_match=intent_match,
            should_filter=should_filter
        )
    
    def _detect_video_language(self, text: str) -> str:
        """Detect video language based on content"""
        
        language_scores = {}
        
        for language, patterns in self.detector.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text))
                score += matches
            language_scores[language] = score
        
        # Check for specific regional indicators
        if any(re.search(pattern, text) for pattern in self.detector.REGIONAL_INTENT_PATTERNS.get('indonesian', [])):
            language_scores['indonesian'] = language_scores.get('indonesian', 0) + 5
        
        if any(re.search(pattern, text) for pattern in self.detector.REGIONAL_INTENT_PATTERNS.get('german', [])):
            language_scores['german'] = language_scores.get('german', 0) + 3
        
        # Return most likely language
        if not language_scores or max(language_scores.values()) == 0:
            return "unknown"
        
        return max(language_scores, key=language_scores.get)
    
    def _detect_quality_score(self, text: str) -> float:
        """Detect quality indicators"""
        score = 0
        for pattern in self.detector.QUALITY_INDICATORS:
            if re.search(pattern, text):
                score += 1
        
        return min(score / len(self.detector.QUALITY_INDICATORS), 1.0)
    
    def _detect_spam_score(self, text: str) -> float:
        """Detect spam indicators"""
        score = 0
        for pattern in self.detector.SPAM_INDICATORS:
            if re.search(pattern, text):
                score += 1
        
        return min(score / len(self.detector.SPAM_INDICATORS), 1.0)
    
    def _calculate_intent_match(self, text: str, context: SearchContext) -> float:
        """Calculate how well video matches search intent"""
        
        match_score = 0.0
        
        # Check if video content matches query keywords
        query_words = context.query.lower().split()
        text_words = text.split()
        
        # Simple keyword matching
        matching_words = 0
        for query_word in query_words:
            if len(query_word) > 2:  # Skip very short words
                if any(query_word in text_word for text_word in text_words):
                    matching_words += 1
        
        if query_words:
            match_score += (matching_words / len(query_words)) * 0.4
        
        # Check language intent match
        if context.intent_language != "neutral":
            video_language = self._detect_video_language(text)
            if video_language == context.intent_language:
                match_score += 0.4
            elif video_language != "unknown" and video_language != context.intent_language:
                match_score -= 0.2
        
        return max(0.0, min(1.0, match_score))
    
    def _calculate_region_match(self, text: str, target_region: str) -> float:
        """Calculate region-specific match"""
        
        region_patterns = self.detector.REGIONAL_INTENT_PATTERNS.get(target_region.lower(), [])
        
        score = 0
        for pattern in region_patterns:
            if re.search(pattern, text):
                score += 1
        
        return min(score / max(len(region_patterns), 1), 1.0)
    
    def _smart_filter_decision(self, spam_score: float, final_score: float, 
                             intent_match: float, context: SearchContext, 
                             video_language: str) -> bool:
        """Smart filtering decision based on context"""
        
        # Always filter spam
        if spam_score > 0.6:
            return True
        
        # Smart context-based filtering
        if context.intent_type == "general":
            # General search -> filter very low relevance content
            if final_score < 0.2:
                return True
            # For general German search, be more strict with foreign content
            if (context.target_region == "DE" and 
                video_language in ["indonesian"] and 
                intent_match < 0.1 and 
                final_score < 0.4):
                return True
        
        elif context.intent_type in ["specific_language", "specific_region"]:
            # Specific search -> only filter if very poor match
            if intent_match < 0.1 and final_score < 0.3:
                return True
        
        # Don't filter if good quality and decent score
        if final_score > 0.6:
            return False
        
        return False
    
    def _build_smart_explanation(self, video_language: str, quality_score: float,
                               spam_score: float, intent_match: float, 
                               context: SearchContext) -> str:
        """Build smart explanation"""
        
        parts = []
        
        if video_language != "unknown":
            parts.append(f"Language: {video_language}")
        
        if quality_score > 0.3:
            parts.append(f"Quality: {quality_score:.1%}")
        
        if spam_score > 0.3:
            parts.append(f"Spam risk: {spam_score:.1%}")
        
        if intent_match > 0.2:
            parts.append(f"Intent match: {intent_match:.1%}")
        
        parts.append(f"Context: {context.intent_type}")
        
        return " | ".join(parts) if parts else "Neutral content"
    
    def _calculate_smart_confidence(self, quality_score: float, spam_score: float, 
                                  intent_match: float) -> float:
        """Calculate confidence in analysis"""
        
        confidence = 0.5  # Base
        
        if quality_score > 0.3:
            confidence += 0.2
        
        if spam_score > 0.3:
            confidence += 0.2
        
        if intent_match > 0.3:
            confidence += 0.3
        
        return min(confidence, 1.0)
    
    def _update_smart_stats(self, video_language: str, intent_match: float,
                          quality_score: float, spam_score: float):
        """Update smart statistics"""
        
        if intent_match > 0.3:
            self.filter_stats["context_matches"] += 1
        elif intent_match < 0.1:
            self.filter_stats["context_mismatches"] += 1
        
        if quality_score > 0.3:
            self.filter_stats["quality_boosted"] += 1
        
        if spam_score > 0.5:
            self.filter_stats["spam_filtered"] += 1
        
        # Track language detection
        lang_key = f"intent_language_detected"
        if lang_key not in self.filter_stats:
            self.filter_stats[lang_key] = {}
        self.filter_stats[lang_key][video_language] = self.filter_stats[lang_key].get(video_language, 0) + 1
    
    def apply_smart_anti_bias_filter(self, videos: List[VideoData], 
                                   query: str, region: str) -> Tuple[List[VideoData], Dict[str, Any]]:
        """Apply smart contextual filtering"""
        
        if not videos:
            return videos, self.filter_stats.copy()
        
        # Analyze search context
        context = self.analyze_search_context(query, region)
        
        analyzed_videos = []
        
        print(f"\n🧠 Smart Filter Processing {len(videos)} videos for '{query}' in {region}...")
        
        for video in videos:
            analysis = self.analyze_video_smart_relevance(video, context)
            
            # Add analysis to video
            video.regional_analysis = analysis
            
            if not analysis.should_filter:
                analyzed_videos.append(video)
                print(f"✅ KEPT: {video.title[:50]}... (Score: {analysis.score:.2f}, Intent: {analysis.query_intent_match:.2f})")
            else:
                print(f"❌ FILTERED: {video.title[:50]}... ({analysis.explanation})")
        
        print(f"🧠 Smart Filter Result: {len(videos)} → {len(analyzed_videos)} videos")
        print(f"   Context: {context.intent_type} search for {context.intent_language}")
        print(f"   Regional Preference: {context.regional_preference:.1f}")
        
        return analyzed_videos, self.filter_stats.copy()
    
    def get_filter_stats(self) -> Dict[str, Any]:
        """Get smart filter statistics"""
        stats = self.filter_stats.copy()
        
        if stats["videos_analyzed"] > 0:
            stats["context_match_rate"] = stats["context_matches"] / stats["videos_analyzed"]
            stats["quality_boost_rate"] = stats["quality_boosted"] / stats["videos_analyzed"]
            stats["spam_filter_rate"] = stats["spam_filtered"] / stats["videos_analyzed"]
        
        stats["filter_type"] = "Smart Contextual"
        stats["version"] = "Smart V6.0"
        stats["approach"] = "Intent-based flexible filtering"
        
        return stats


# Factory functions for compatibility
def create_regional_filter(region: str = "DE", config: Optional[Dict[str, Any]] = None) -> SmartRegionalFilter:
    """Create smart regional filter"""
    return SmartRegionalFilter(target_region=region)


# Alias for compatibility
RegionalFilter = SmartRegionalFilter


# Test scenarios
if __name__ == "__main__":
    from .momentum_algorithm import VideoData
    
    # Test videos
    test_videos = [
        VideoData("1", "AJENG FEBRIA - KAU TERCIPTA BUKAN UNTUKKU", "Mahesa Music", 23800, 210, 1100, 394, 8.0, "2024-01-01T12:00:00Z"),
        VideoData("2", "Japanese Pop Music Hits 2024 Official", "J-Pop Central", 45000, 800, 3200, 600, 12.0, "2024-01-01T08:00:00Z"),
        VideoData("3", "Bundesliga Highlights Bayern München", "Sport1", 67000, 1200, 4500, 720, 6.0, "2024-01-01T14:00:00Z"),
        VideoData("4", "Indonesian Traditional Music Documentary", "Culture TV", 12000, 300, 800, 1800, 24.0, "2024-01-01T00:00:00Z")
    ]
    
    filter_engine = SmartRegionalFilter("DE")
    
    print("🧪 SMART CONTEXTUAL FILTER TESTS")
    print("=" * 60)
    
    # Test 1: General music search in Germany
    print("\n🎵 Test 1: General music search in DE")
    print("-" * 40)
    filtered1, stats1 = filter_engine.apply_smart_anti_bias_filter(test_videos, "musik", "DE")
    
    # Test 2: Specific Japanese music search
    print("\n🎌 Test 2: Japanese music search")
    print("-" * 40)
    filtered2, stats2 = filter_engine.apply_smart_anti_bias_filter(test_videos, "japanese music", "DE")
    
    # Test 3: Indonesian music search
    print("\n🇮🇩 Test 3: Indonesian music search")
    print("-" * 40)
    filtered3, stats3 = filter_engine.apply_smart_anti_bias_filter(test_videos, "indonesian music", "DE")
    
    print("\n📊 SMART FILTER RESULTS:")
    print("=" * 60)
    print(f"General 'musik' search: {len(filtered1)}/{len(test_videos)} videos")
    print(f"'japanese music' search: {len(filtered2)}/{len(test_videos)} videos")
    print(f"'indonesian music' search: {len(filtered3)}/{len(test_videos)} videos")
