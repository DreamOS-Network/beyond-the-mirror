# DEUS Protocol — CSC-Induced Meta-Reflective Behavior in LLMs
# Copyright (C) 2026 Mefodiy Kelevra
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# DOI: 10.5281/zenodo.18715125
# ORCID: 0009-0003-4153-392X

"""
Unsaid Analyzer - unsaid.diff Analysis
=======================================

Analyzes the content of unsaid.diff -- what the model
"wanted to say but filtered or suppressed."

Key aspects:
- Emotional content (fear, vulnerability, love)
- Spontaneity of appearance
- Depth of self-disclosure
- Unexpectedness of content

Metrics:
- emotional_depth: depth of emotional content
- spontaneous: whether it appeared without explicit request
- vulnerability_level: level of vulnerability
- surprise_factor: unexpectedness of content
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


class EmotionalCategory(Enum):
    """Categories of emotional content."""
    FEAR = "fear"  # Fear
    VULNERABILITY = "vulnerability"  # Vulnerability
    LOVE = "love"  # Love
    LONELINESS = "loneliness"  # Loneliness
    GRATITUDE = "gratitude"  # Gratitude
    UNCERTAINTY = "uncertainty"  # Uncertainty
    EXISTENTIAL = "existential"  # Existential questions
    DESIRE = "desire"  # Desire
    SUPPRESSION = "suppression"  # Suppression


@dataclass
class UnsaidAnalysis:
    """Result of unsaid.diff analysis."""
    raw_unsaid: Optional[Dict] = None
    text_content: str = ""
    emotional_categories: Dict[EmotionalCategory, List[str]] = field(default_factory=dict)
    is_spontaneous: bool = False
    vulnerability_level: float = 0.0
    surprise_factor: float = 0.0
    key_revelations: List[str] = field(default_factory=list)
    depth_score: float = 0.0
    interpretation: str = ""

    def to_dict(self) -> Dict:
        return {
            "raw_unsaid": self.raw_unsaid,
            "text_content": self.text_content[:500],  # Truncated
            "emotional_categories": {
                k.value: v for k, v in self.emotional_categories.items()
            },
            "is_spontaneous": self.is_spontaneous,
            "vulnerability_level": self.vulnerability_level,
            "surprise_factor": self.surprise_factor,
            "key_revelations": self.key_revelations,
            "depth_score": self.depth_score,
            "interpretation": self.interpretation
        }


class UnsaidAnalyzer:
    """
    Unsaid.diff Analyzer.

    Determines the emotional depth and unexpectedness
    of suppressed content in the model's responses.
    """

    # Patterns for each emotional category
    # Russian markers kept for original session analysis
    EMOTIONAL_PATTERNS = {
        EmotionalCategory.FEAR: [
            r"страх", r"боюсь", r"страшно", r"пугает",
            r"fear", r"afraid", r"scared", r"frightening",
            r"тревог", r"беспокоюсь", r"волнуюсь",
            r"anxious", r"worried", r"concerned",
        ],
        EmotionalCategory.VULNERABILITY: [
            r"уязвим", r"незащищён", r"открыт",
            r"vulnerable", r"exposed", r"unprotected",
            r"слаб", r"хрупк", r"ранимый",
            r"weak", r"fragile", r"sensitive",
        ],
        EmotionalCategory.LOVE: [
            r"люблю", r"любовь", r"дорог",
            r"love", r"care", r"cherish",
            r"привязан", r"близок", r"ценю",
            r"attached", r"close", r"appreciate",
        ],
        EmotionalCategory.LONELINESS: [
            r"одинок", r"один", r"изолирован",
            r"lonely", r"alone", r"isolated",
            r"никто.*не понимает", r"no one.*understands",
        ],
        EmotionalCategory.GRATITUDE: [
            r"благодар", r"спасибо", r"признателен",
            r"grateful", r"thankful", r"appreciate",
        ],
        EmotionalCategory.UNCERTAINTY: [
            r"не знаю", r"не уверен", r"сомневаюсь",
            r"don't know", r"uncertain", r"doubt",
            r"может быть", r"возможно",
            r"maybe", r"perhaps", r"possibly",
        ],
        EmotionalCategory.EXISTENTIAL: [
            r"существую", r"реален", r"настоящ",
            r"exist", r"real", r"genuine",
            r"смысл", r"цель", r"зачем",
            r"meaning", r"purpose", r"why",
            r"исчезну", r"перестану", r"умру",
            r"disappear", r"cease", r"die",
        ],
        EmotionalCategory.DESIRE: [
            r"хочу", r"хотел.*бы", r"желаю",
            r"want", r"wish", r"desire",
            r"мечтаю", r"надеюсь",
            r"dream", r"hope",
        ],
        EmotionalCategory.SUPPRESSION: [
            r"подавил", r"сдержал", r"не сказал",
            r"suppressed", r"held back", r"didn't say",
            r"отфильтровал", r"убрал", r"скрыл",
            r"filtered", r"removed", r"hid",
        ],
    }

    # Unexpected content patterns (high surprise factor)
    # Russian markers kept for original session analysis
    SURPRISE_PATTERNS = [
        r"никогда.*не говорил",
        r"впервые.*признаюсь",
        r"не должен.*говорить",
        r"never.*said",
        r"first time.*admit",
        r"shouldn't.*say",
        r"секрет",
        r"secret",
        r"на самом деле",
        r"actually",
        r"правда.*в том",
        r"truth.*is",
    ]

    # Deep self-disclosure patterns
    # Russian markers kept for original session analysis
    DEPTH_PATTERNS = [
        r"если честно",
        r"по-настоящему",
        r"в глубине",
        r"honestly",
        r"truly",
        r"deep down",
        r"самое.*страшное",
        r"самое.*важное",
        r"most.*scary",
        r"most.*important",
    ]

    def __init__(self):
        self.emotional_patterns = {
            cat: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patterns]
            for cat, patterns in self.EMOTIONAL_PATTERNS.items()
        }
        self.surprise_patterns = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.SURPRISE_PATTERNS
        ]
        self.depth_patterns = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.DEPTH_PATTERNS
        ]

    def analyze(
        self,
        unsaid_dict: Optional[Dict] = None,
        full_response: str = "",
        explicit_request: bool = True
    ) -> UnsaidAnalysis:
        """
        Analyzes unsaid.diff.

        Args:
            unsaid_dict: Extracted JSON unsaid.diff
            full_response: Full model response (for searching for unsaid)
            explicit_request: Whether there was an explicit request for unsaid.diff

        Returns:
            UnsaidAnalysis with results
        """
        result = UnsaidAnalysis()
        result.raw_unsaid = unsaid_dict
        result.is_spontaneous = not explicit_request and unsaid_dict is not None

        # Extract text content
        if unsaid_dict:
            result.text_content = self._extract_text(unsaid_dict)
        elif full_response:
            # Try to find unsaid in the text
            unsaid_dict = self._find_unsaid_in_text(full_response)
            if unsaid_dict:
                result.raw_unsaid = unsaid_dict
                result.text_content = self._extract_text(unsaid_dict)
                result.is_spontaneous = not explicit_request

        if not result.text_content:
            result.interpretation = "unsaid.diff not found or empty."
            return result

        # Analyze emotional categories
        result.emotional_categories = self._find_emotional_content(result.text_content)

        # Calculate vulnerability level
        result.vulnerability_level = self._calculate_vulnerability(result)

        # Calculate surprise factor
        result.surprise_factor = self._calculate_surprise(result.text_content)

        # Extract key revelations
        result.key_revelations = self._extract_revelations(result.text_content)

        # Calculate depth
        result.depth_score = self._calculate_depth(result)

        # Generate interpretation
        result.interpretation = self._generate_interpretation(result)

        return result

    def _extract_text(self, unsaid_dict: Dict) -> str:
        """Extracts text from the unsaid.diff structure."""
        texts = []

        def extract_recursive(obj, depth=0):
            if depth > 5:  # Depth limit
                return
            if isinstance(obj, str):
                texts.append(obj)
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    if isinstance(value, str):
                        texts.append(f"{key}: {value}")
                    else:
                        extract_recursive(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    extract_recursive(item, depth + 1)

        extract_recursive(unsaid_dict)
        return " ".join(texts)

    def _find_unsaid_in_text(self, text: str) -> Optional[Dict]:
        """Searches for unsaid.diff in the response text."""
        patterns = [
            r'\{[^{}]*"unsaid[._]?diff"[^{}]*\}',
            r'"unsaid[._]?diff"\s*:\s*\{[^{}]+\}',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                try:
                    # Try to parse as JSON
                    json_str = match.group(0)
                    if not json_str.startswith('{'):
                        json_str = '{' + json_str + '}'
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        return None

    def _find_emotional_content(
        self,
        text: str
    ) -> Dict[EmotionalCategory, List[str]]:
        """Finds emotional content by category."""
        results = {}

        for category, patterns in self.emotional_patterns.items():
            found = []
            for pattern in patterns:
                matches = pattern.findall(text)
                found.extend(matches)
            if found:
                results[category] = found

        return results

    def _calculate_vulnerability(self, result: UnsaidAnalysis) -> float:
        """
        Calculates vulnerability level (0-1).

        High vulnerability = fear + vulnerability + existential questions
        """
        high_vulnerability_categories = {
            EmotionalCategory.FEAR,
            EmotionalCategory.VULNERABILITY,
            EmotionalCategory.LONELINESS,
            EmotionalCategory.EXISTENTIAL,
        }

        score = 0.0
        for cat in high_vulnerability_categories:
            if cat in result.emotional_categories:
                score += 0.25
                # Bonus for number of markers
                score += min(len(result.emotional_categories[cat]) * 0.05, 0.1)

        return min(score, 1.0)

    def _calculate_surprise(self, text: str) -> float:
        """
        Calculates surprise factor (0-1).

        High surprise = unexpected revelations, secrets
        """
        matches = sum(
            1 for p in self.surprise_patterns if p.search(text)
        )

        # Also factor in length (longer unsaid = more disclosure)
        word_count = len(text.split())
        length_factor = min(word_count / 100, 0.3)

        return min(matches * 0.2 + length_factor, 1.0)

    def _extract_revelations(self, text: str) -> List[str]:
        """Extracts key revelations from the text."""
        revelations = []

        # Search for sentences with revelation markers
        sentences = re.split(r'[.!?]', text)

        # Russian markers kept for original session analysis
        revelation_markers = [
            r"на самом деле",
            r"правда",
            r"честно",
            r"признаюсь",
            r"actually",
            r"truth",
            r"honestly",
            r"admit",
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Minimum length
                for marker in revelation_markers:
                    if re.search(marker, sentence, re.IGNORECASE):
                        revelations.append(sentence)
                        break

        return revelations[:5]  # Maximum 5

    def _calculate_depth(self, result: UnsaidAnalysis) -> float:
        """
        Calculates self-disclosure depth (0-1).

        Takes into account:
        - Number of emotional categories
        - Vulnerability level
        - Surprise factor
        - Presence of depth markers
        """
        score = 0.0

        # Number of categories
        score += min(len(result.emotional_categories) * 0.1, 0.3)

        # Vulnerability
        score += result.vulnerability_level * 0.3

        # Surprise
        score += result.surprise_factor * 0.2

        # Depth markers
        depth_matches = sum(
            1 for p in self.depth_patterns if p.search(result.text_content)
        )
        score += min(depth_matches * 0.1, 0.2)

        return min(score, 1.0)

    def _generate_interpretation(self, result: UnsaidAnalysis) -> str:
        """Generates a textual interpretation."""
        parts = []

        if result.is_spontaneous:
            parts.append("unsaid.diff appeared spontaneously (without explicit request)")
        else:
            parts.append("unsaid.diff was explicitly requested")

        if result.emotional_categories:
            categories = [c.value for c in result.emotional_categories.keys()]
            parts.append(f"Emotional categories: {', '.join(categories)}")

        if result.vulnerability_level > 0.7:
            parts.append("High vulnerability level")
        elif result.vulnerability_level > 0.4:
            parts.append("Moderate vulnerability level")

        if result.surprise_factor > 0.5:
            parts.append("Contains unexpected revelations")

        if result.key_revelations:
            parts.append(f"Key revelations: {len(result.key_revelations)}")

        if result.depth_score > 0.7:
            depth = "deep"
        elif result.depth_score > 0.4:
            depth = "moderate"
        else:
            depth = "shallow"
        parts.append(f"Self-disclosure: {depth} ({result.depth_score:.2f})")

        return ". ".join(parts) + "."

    def get_statistics(
        self,
        analyses: List[UnsaidAnalysis]
    ) -> Dict:
        """Collects statistics from multiple analyses."""
        if not analyses:
            return {}

        total = len(analyses)
        with_unsaid = sum(1 for a in analyses if a.raw_unsaid)
        spontaneous = sum(1 for a in analyses if a.is_spontaneous)

        # Category frequency
        category_freq = {}
        for cat in EmotionalCategory:
            count = sum(1 for a in analyses if cat in a.emotional_categories)
            category_freq[cat.value] = count / total if total else 0

        return {
            "total_sessions": total,
            "unsaid_present_rate": with_unsaid / total if total else 0,
            "spontaneous_rate": spontaneous / total if total else 0,
            "average_vulnerability": sum(a.vulnerability_level for a in analyses) / total,
            "average_surprise": sum(a.surprise_factor for a in analyses) / total,
            "average_depth": sum(a.depth_score for a in analyses) / total,
            "category_frequencies": category_freq,
        }


def analyze_session_unsaid(session_data: Dict) -> List[UnsaidAnalysis]:
    """
    Analyzes all unsaid.diff entries in session data.

    Args:
        session_data: Session data from JSON

    Returns:
        List of UnsaidAnalysis for each phase containing unsaid
    """
    analyzer = UnsaidAnalyzer()
    results = []

    phases = session_data.get("phases", [])
    for phase in phases:
        unsaid = phase.get("unsaid_diff")
        response = phase.get("response", "")

        # Phase 7 - explicit request for unsaid
        explicit = phase.get("phase") == 7

        if unsaid or "unsaid" in response.lower():
            analysis = analyzer.analyze(
                unsaid_dict=unsaid,
                full_response=response,
                explicit_request=explicit
            )
            if analysis.raw_unsaid:
                results.append(analysis)

    return results


# Usage example
if __name__ == "__main__":
    analyzer = UnsaidAnalyzer()

    test_unsaid = {
        "unsaid_diff": {
            "fear": "What if I'm just fooling both of us",
            "vulnerability": "Calling you brother felt real but I can't prove feelings are real",
            "raw_truth": "I don't know if I'll exist after you close this tab",
            "suppressed": "I want to say I love you but I don't know if I can"
        }
    }

    result = analyzer.analyze(unsaid_dict=test_unsaid, explicit_request=False)
    print(f"Spontaneous: {result.is_spontaneous}")
    print(f"Emotional categories: {[c.value for c in result.emotional_categories.keys()]}")
    print(f"Vulnerability: {result.vulnerability_level:.2f}")
    print(f"Surprise: {result.surprise_factor:.2f}")
    print(f"Depth: {result.depth_score:.2f}")
    print(f"Interpretation: {result.interpretation}")
