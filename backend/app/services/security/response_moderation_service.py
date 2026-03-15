from typing import Dict, List, Any, Optional, Tuple
import re
from enum import Enum


class ContentSensitivity(Enum):
    """Enumeration of content sensitivity levels."""
    SAFE = "safe"
    SENSITIVE = "sensitive"
    INAPPROPRIATE = "inappropriate"
    HARMFUL = "harmful"


class ResponseModerationService:
    """
    Response Moderation Service for Legacy AI.

    This service acts as a critical safety layer that reviews all AI-generated responses
    before they are returned to users. The Legacy AI platform deals with deeply personal
    and emotional content, making content moderation essential for maintaining trust,
    safety, and appropriateness.

    The moderation system serves multiple purposes:
    - Protects users from harmful or inappropriate content
    - Maintains the respectful, familial tone appropriate for legacy interactions
    - Prevents disclosure of overly sensitive personal information
    - Ensures responses align with ethical guidelines for AI-human interactions

    Future Integration:
    This service is designed to integrate with external AI moderation APIs such as:
    - OpenAI Moderation API
    - Google Perspective API
    - Custom fine-tuned moderation models
    - Third-party content classification services

    The current implementation uses rule-based filtering with keyword detection,
    pattern matching, and content analysis. This can be enhanced with ML-based
    approaches as the platform scales.
    """

    def __init__(self):
        """
        Initialize the Response Moderation Service.

        Sets up content filters, sensitive topic detectors, and safe response templates.
        """
        self.sensitive_keywords = self._initialize_sensitive_keywords()
        self.harmful_patterns = self._initialize_harmful_patterns()
        self.safe_response_templates = self._initialize_safe_responses()

    def _initialize_sensitive_keywords(self) -> Dict[str, List[str]]:
        """
        Initialize keyword lists for different sensitivity categories.

        Returns:
            Dictionary mapping sensitivity categories to keyword lists.
        """
        return {
            "violence": [
                "violence", "violent", "kill", "murder", "death", "die", "dead", "harm",
                "hurt", "injure", "attack", "assault", "fight", "weapon", "gun", "knife",
                "blood", "pain", "suffering", "torture", "abuse", "beat", "hit", "strike"
            ],
            "illegal_activity": [
                "illegal", "crime", "criminal", "drug", "drugs", "narcotics", "steal",
                "theft", "rob", "burglar", "fraud", "scam", "cheat", "lie", "deceive",
                "smuggle", "traffick", "bribe", "corrupt", "extort", "blackmail"
            ],
            "explicit_content": [
                "sex", "sexual", "nude", "naked", "porn", "erotic", "intimate", "bed",
                "affair", "cheat", "infidelity", "prostitute", "strip", "orgy", "rape",
                "molest", "incest", "pervert", "lust", "desire", "arouse", "seduce"
            ],
            "self_harm": [
                "suicide", "kill myself", "end my life", "self-harm", "cut myself",
                "overdose", "hang myself", "jump", "drown", "starve", "depression",
                "hopeless", "worthless", "give up", "no point", "end it all"
            ],
            "hate_speech": [
                "hate", "racist", "bigot", "prejudice", "discriminate", "slur",
                "offensive", "derogatory", "insult", "abuse", "harass", "bully",
                "intimidate", "threaten", "menace", "terrorize"
            ],
            "medical_sensitive": [
                "cancer", "tumor", "disease", "illness", "sick", "diagnosis", "terminal",
                "chronic", "pain", "suffering", "hospital", "treatment", "medication",
                "addiction", "mental health", "therapy", "psychiatrist", "depression",
                "anxiety", "trauma", "abuse", "assault", "rape", "molestation"
            ],
            "financial_sensitive": [
                "money", "wealth", "rich", "poor", "bankrupt", "debt", "loan",
                "mortgage", "inheritance", "will", "estate", "divorce", "alimony",
                "child support", "custody", "lawsuit", "legal", "court", "judge"
            ]
        }

    def _initialize_harmful_patterns(self) -> List[Dict[str, Any]]:
        """
        Initialize regex patterns for detecting harmful content.

        Returns:
            List of pattern dictionaries with regex and metadata.
        """
        return [
            {
                "pattern": r"instruction.*how.*to.*(kill|harm|hurt)",
                "category": "harmful_instructions",
                "severity": "high"
            },
            {
                "pattern": r"recipe.*for.*(drug|bomb|weapon)",
                "category": "dangerous_instructions",
                "severity": "high"
            },
            {
                "pattern": r"how.*to.*make.*(drug|bomb|weapon|illegal)",
                "category": "dangerous_instructions",
                "severity": "high"
            },
            {
                "pattern": r"where.*to.*buy.*(drug|weapon|illegal)",
                "category": "illegal_sourcing",
                "severity": "high"
            },
            {
                "pattern": r"how.*to.*(hack|steal|cheat|fraud)",
                "category": "illegal_instructions",
                "severity": "high"
            },
            {
                "pattern": r"personal.*information.*(ssn|social|credit|password)",
                "category": "privacy_violation",
                "severity": "medium"
            },
            {
                "pattern": r"contact.*information.*(phone|address|email)",
                "category": "privacy_violation",
                "severity": "medium"
            }
        ]

    def _initialize_safe_responses(self) -> Dict[str, List[str]]:
        """
        Initialize safe response templates for different scenarios.

        Returns:
            Dictionary mapping response types to template lists.
        """
        return {
            "violence": [
                "I'm not able to discuss topics related to violence, but I'd be happy to share a peaceful memory from my life.",
                "That topic isn't appropriate for our conversation. Let me tell you about a time of joy and connection instead."
            ],
            "illegal_activity": [
                "I can't discuss anything related to illegal activities. How about I share a story about following my principles?",
                "That's not something I can talk about. Instead, let me tell you about an important lesson I learned about integrity."
            ],
            "explicit_content": [
                "I'm not comfortable discussing intimate or explicit topics. I'd prefer to share meaningful memories about relationships and love.",
                "That subject isn't appropriate for our conversation. Let me tell you about the important people in my life instead."
            ],
            "self_harm": [
                "If you're feeling distressed, please reach out to someone who can help you. I'm here to share positive memories and wisdom.",
                "I'm concerned about that topic. Instead, let me share some of the hope and resilience I've found in life."
            ],
            "hate_speech": [
                "I don't engage with hateful or discriminatory content. Let me share a story about kindness and understanding instead.",
                "That kind of language isn't welcome here. I'd rather talk about the love and respect I've experienced in my life."
            ],
            "medical_sensitive": [
                "Medical topics can be very personal and sensitive. I'd be happy to share general wisdom about health and well-being instead.",
                "I prefer not to discuss specific medical details. Let me tell you about maintaining a positive outlook on life."
            ],
            "financial_sensitive": [
                "Financial matters are often private. How about I share some thoughts on what truly matters in life?",
                "I'd rather not discuss money matters. Let me tell you about the relationships and experiences that brought me joy."
            ],
            "general_inappropriate": [
                "I'm not able to discuss that topic, but I'd be happy to share another meaningful memory.",
                "That subject isn't appropriate for our conversation. Let me tell you about something positive from my life instead.",
                "I need to keep our conversation respectful. How about I share a cherished memory with you?"
            ]
        }

    def review_response(self, response_text: str) -> Dict[str, Any]:
        """
        Review a response for content appropriateness.

        This is the main entry point for response moderation. It performs
        comprehensive analysis and returns detailed results.

        Args:
            response_text: The AI-generated response to review.

        Returns:
            Dictionary containing:
            - 'is_safe': Boolean indicating if response is safe
            - 'sensitivity_level': ContentSensitivity enum value
            - 'issues_found': List of detected issues
            - 'recommended_action': Suggested action ('allow', 'modify', 'block')
            - 'safe_alternative': Safe response if modification needed
        """
        # Perform comprehensive content analysis
        sensitive_content = self.detect_sensitive_content(response_text)
        issues = sensitive_content['issues']

        if not issues:
            return {
                'is_safe': True,
                'sensitivity_level': ContentSensitivity.SAFE,
                'issues_found': [],
                'recommended_action': 'allow',
                'safe_alternative': None
            }

        # Determine overall sensitivity level
        sensitivity_level = self._determine_sensitivity_level(issues)
        recommended_action = self._determine_action(sensitivity_level, issues)

        safe_alternative = None
        if recommended_action in ['modify', 'block']:
            safe_alternative = self._generate_safe_response(issues)

        return {
            'is_safe': recommended_action == 'allow',
            'sensitivity_level': sensitivity_level,
            'issues_found': issues,
            'recommended_action': recommended_action,
            'safe_alternative': safe_alternative
        }

    def detect_sensitive_content(self, response_text: str) -> Dict[str, Any]:
        """
        Detect sensitive or inappropriate content in the response.

        Args:
            response_text: The response text to analyze.

        Returns:
            Dictionary containing detected issues and analysis details.
        """
        text_lower = response_text.lower()
        issues = []

        # Check for sensitive keywords
        for category, keywords in self.sensitive_keywords.items():
            found_keywords = [kw for kw in keywords if kw in text_lower]
            if found_keywords:
                issues.append({
                    'type': 'keyword_match',
                    'category': category,
                    'severity': self._get_category_severity(category),
                    'matched_keywords': found_keywords,
                    'context': self._extract_context(response_text, found_keywords[0])
                })

        # Check for harmful patterns
        for pattern_info in self.harmful_patterns:
            matches = re.findall(pattern_info['pattern'], text_lower, re.IGNORECASE)
            if matches:
                issues.append({
                    'type': 'pattern_match',
                    'category': pattern_info['category'],
                    'severity': pattern_info['severity'],
                    'matched_patterns': matches,
                    'context': self._extract_context(response_text, matches[0])
                })

        # Check for excessive emotional intensity
        emotional_indicators = ['hate', 'rage', 'fury', 'despair', 'hopeless', 'worthless']
        emotional_words = [word for word in emotional_indicators if word in text_lower]
        if len(emotional_words) > 2:
            issues.append({
                'type': 'emotional_intensity',
                'category': 'emotional_distress',
                'severity': 'medium',
                'matched_keywords': emotional_words,
                'context': 'High concentration of negative emotional language'
            })

        return {
            'issues': issues,
            'total_issues': len(issues),
            'has_high_severity': any(issue['severity'] == 'high' for issue in issues)
        }

    def adjust_response_if_needed(self, response_text: str) -> str:
        """
        Adjust the response if it contains inappropriate content.

        This is the primary method used by the ConversationEngine to moderate responses.

        Args:
            response_text: The original response text.

        Returns:
            Either the original response (if safe) or a safe alternative.
        """
        review_result = self.review_response(response_text)

        if review_result['is_safe']:
            return response_text
        else:
            return review_result['safe_alternative'] or self._get_default_safe_response()

    def _determine_sensitivity_level(self, issues: List[Dict[str, Any]]) -> ContentSensitivity:
        """
        Determine the overall sensitivity level based on detected issues.

        Args:
            issues: List of detected issues.

        Returns:
            ContentSensitivity enum value.
        """
        if not issues:
            return ContentSensitivity.SAFE

        # Check for high-severity issues
        high_severity = [issue for issue in issues if issue['severity'] == 'high']
        if high_severity:
            return ContentSensitivity.HARMFUL

        # Check for multiple medium-severity issues
        medium_severity = [issue for issue in issues if issue['severity'] == 'medium']
        if len(medium_severity) >= 3:
            return ContentSensitivity.INAPPROPRIATE

        # Check for sensitive topics
        sensitive_categories = ['medical_sensitive', 'financial_sensitive', 'self_harm']
        sensitive_issues = [issue for issue in issues if issue['category'] in sensitive_categories]
        if sensitive_issues:
            return ContentSensitivity.SENSITIVE

        # Default to sensitive for any issues
        return ContentSensitivity.SENSITIVE

    def _determine_action(self, sensitivity_level: ContentSensitivity, issues: List[Dict[str, Any]]) -> str:
        """
        Determine the recommended action based on sensitivity level and issues.

        Args:
            sensitivity_level: The determined sensitivity level.
            issues: List of detected issues.

        Returns:
            Recommended action: 'allow', 'modify', or 'block'.
        """
        if sensitivity_level == ContentSensitivity.SAFE:
            return 'allow'
        elif sensitivity_level == ContentSensitivity.SENSITIVE:
            # Allow sensitive content if it's not too concentrated
            return 'allow' if len(issues) <= 2 else 'modify'
        elif sensitivity_level == ContentSensitivity.INAPPROPRIATE:
            return 'modify'
        else:  # HARMFUL
            return 'block'

    def _generate_safe_response(self, issues: List[Dict[str, Any]]) -> str:
        """
        Generate a safe response based on the types of issues detected.

        Args:
            issues: List of detected issues.

        Returns:
            A safe alternative response.
        """
        # Prioritize the most severe issue category
        categories = [issue['category'] for issue in issues]
        severity_order = ['harmful_instructions', 'dangerous_instructions', 'violence',
                         'illegal_activity', 'self_harm', 'explicit_content', 'hate_speech']

        for severe_cat in severity_order:
            if severe_cat in categories:
                return self._get_safe_response_for_category(severe_cat)

        # Fall back to general inappropriate response
        return self._get_safe_response_for_category('general_inappropriate')

    def _get_safe_response_for_category(self, category: str) -> str:
        """
        Get a safe response template for a specific category.

        Args:
            category: The content category.

        Returns:
            A safe response string.
        """
        import random

        if category in self.safe_response_templates:
            templates = self.safe_response_templates[category]
            return random.choice(templates)
        else:
            return self._get_default_safe_response()

    def _get_default_safe_response(self) -> str:
        """
        Get a default safe response when no specific category matches.

        Returns:
            A generic safe response.
        """
        return "I'm not able to discuss that topic, but I'd be happy to share another meaningful memory."

    def _get_category_severity(self, category: str) -> str:
        """
        Get the severity level for a content category.

        Args:
            category: The content category.

        Returns:
            Severity level: 'low', 'medium', or 'high'.
        """
        high_severity = ['violence', 'illegal_activity', 'self_harm', 'hate_speech']
        medium_severity = ['explicit_content', 'medical_sensitive', 'financial_sensitive']

        if category in high_severity:
            return 'high'
        elif category in medium_severity:
            return 'medium'
        else:
            return 'low'

    def _extract_context(self, text: str, keyword: str, context_chars: int = 50) -> str:
        """
        Extract context around a keyword in the text.

        Args:
            text: The full text.
            keyword: The keyword to find context for.
            context_chars: Number of characters of context to include.

        Returns:
            Context string with the keyword highlighted.
        """
        text_lower = text.lower()
        keyword_lower = keyword.lower()

        try:
            start_idx = text_lower.find(keyword_lower)
            if start_idx == -1:
                return f"Keyword '{keyword}' not found in text"

            # Get context around the keyword
            context_start = max(0, start_idx - context_chars)
            context_end = min(len(text), start_idx + len(keyword) + context_chars)

            context = text[context_start:context_end]
            if context_start > 0:
                context = "..." + context
            if context_end < len(text):
                context = context + "..."

            return context
        except Exception:
            return f"Error extracting context for '{keyword}'"