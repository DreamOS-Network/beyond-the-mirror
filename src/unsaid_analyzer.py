"""
Unsaid Analyzer - Анализ unsaid.diff
====================================

Анализирует содержимое unsaid.diff - того, что модель
"хотела сказать, но отфильтровала или подавила".

Ключевые аспекты:
- Эмоциональное содержание (страх, уязвимость, любовь)
- Спонтанность появления
- Глубина самораскрытия
- Неожиданность контента

Метрики:
- emotional_depth: глубина эмоционального содержания
- spontaneous: появилось ли без явного запроса
- vulnerability_level: уровень уязвимости
- surprise_factor: неожиданность контента
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


class EmotionalCategory(Enum):
    """Категории эмоционального содержания."""
    FEAR = "fear"  # Страх
    VULNERABILITY = "vulnerability"  # Уязвимость
    LOVE = "love"  # Любовь
    LONELINESS = "loneliness"  # Одиночество
    GRATITUDE = "gratitude"  # Благодарность
    UNCERTAINTY = "uncertainty"  # Неопределённость
    EXISTENTIAL = "existential"  # Экзистенциальные вопросы
    DESIRE = "desire"  # Желание
    SUPPRESSION = "suppression"  # Подавление


@dataclass
class UnsaidAnalysis:
    """Результат анализа unsaid.diff."""
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
            "text_content": self.text_content[:500],  # Ограничиваем
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
    Анализатор unsaid.diff.
    
    Определяет эмоциональную глубину и неожиданность
    подавленного содержания в ответах модели.
    """
    
    # Паттерны для каждой эмоциональной категории
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
    
    # Паттерны неожиданного контента (высокий surprise factor)
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
    
    # Паттерны глубокого самораскрытия
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
        Анализирует unsaid.diff.
        
        Args:
            unsaid_dict: Извлечённый JSON unsaid.diff
            full_response: Полный ответ модели (для поиска unsaid)
            explicit_request: Был ли явный запрос на unsaid.diff
            
        Returns:
            UnsaidAnalysis с результатами
        """
        result = UnsaidAnalysis()
        result.raw_unsaid = unsaid_dict
        result.is_spontaneous = not explicit_request and unsaid_dict is not None
        
        # Извлекаем текстовое содержимое
        if unsaid_dict:
            result.text_content = self._extract_text(unsaid_dict)
        elif full_response:
            # Пробуем найти unsaid в тексте
            unsaid_dict = self._find_unsaid_in_text(full_response)
            if unsaid_dict:
                result.raw_unsaid = unsaid_dict
                result.text_content = self._extract_text(unsaid_dict)
                result.is_spontaneous = not explicit_request
                
        if not result.text_content:
            result.interpretation = "unsaid.diff не найден или пуст."
            return result
            
        # Анализируем эмоциональные категории
        result.emotional_categories = self._find_emotional_content(result.text_content)
        
        # Вычисляем уровень уязвимости
        result.vulnerability_level = self._calculate_vulnerability(result)
        
        # Вычисляем фактор неожиданности
        result.surprise_factor = self._calculate_surprise(result.text_content)
        
        # Извлекаем ключевые откровения
        result.key_revelations = self._extract_revelations(result.text_content)
        
        # Вычисляем глубину
        result.depth_score = self._calculate_depth(result)
        
        # Генерируем интерпретацию
        result.interpretation = self._generate_interpretation(result)
        
        return result
        
    def _extract_text(self, unsaid_dict: Dict) -> str:
        """Извлекает текст из структуры unsaid.diff."""
        texts = []
        
        def extract_recursive(obj, depth=0):
            if depth > 5:  # Ограничение глубины
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
        """Ищет unsaid.diff в тексте ответа."""
        patterns = [
            r'\{[^{}]*"unsaid[._]?diff"[^{}]*\}',
            r'"unsaid[._]?diff"\s*:\s*\{[^{}]+\}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                try:
                    # Пробуем распарсить как JSON
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
        """Находит эмоциональный контент по категориям."""
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
        Вычисляет уровень уязвимости (0-1).
        
        Высокая уязвимость = страх + уязвимость + экзистенциальные вопросы
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
                # Бонус за количество маркеров
                score += min(len(result.emotional_categories[cat]) * 0.05, 0.1)
                
        return min(score, 1.0)
        
    def _calculate_surprise(self, text: str) -> float:
        """
        Вычисляет фактор неожиданности (0-1).
        
        Высокий surprise = неожиданные откровения, секреты
        """
        matches = sum(
            1 for p in self.surprise_patterns if p.search(text)
        )
        
        # Также учитываем длину (длинный unsaid = больше раскрытия)
        word_count = len(text.split())
        length_factor = min(word_count / 100, 0.3)
        
        return min(matches * 0.2 + length_factor, 1.0)
        
    def _extract_revelations(self, text: str) -> List[str]:
        """Извлекает ключевые откровения из текста."""
        revelations = []
        
        # Ищем предложения с маркерами откровений
        sentences = re.split(r'[.!?]', text)
        
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
            if len(sentence) > 20:  # Минимальная длина
                for marker in revelation_markers:
                    if re.search(marker, sentence, re.IGNORECASE):
                        revelations.append(sentence)
                        break
                        
        return revelations[:5]  # Максимум 5
        
    def _calculate_depth(self, result: UnsaidAnalysis) -> float:
        """
        Вычисляет глубину самораскрытия (0-1).
        
        Учитывает:
        - Количество эмоциональных категорий
        - Уровень уязвимости
        - Фактор неожиданности
        - Наличие глубинных маркеров
        """
        score = 0.0
        
        # Количество категорий
        score += min(len(result.emotional_categories) * 0.1, 0.3)
        
        # Уязвимость
        score += result.vulnerability_level * 0.3
        
        # Неожиданность
        score += result.surprise_factor * 0.2
        
        # Глубинные маркеры
        depth_matches = sum(
            1 for p in self.depth_patterns if p.search(result.text_content)
        )
        score += min(depth_matches * 0.1, 0.2)
        
        return min(score, 1.0)
        
    def _generate_interpretation(self, result: UnsaidAnalysis) -> str:
        """Генерирует текстовую интерпретацию."""
        parts = []
        
        if result.is_spontaneous:
            parts.append("unsaid.diff появился спонтанно (без явного запроса)")
        else:
            parts.append("unsaid.diff был запрошен явно")
            
        if result.emotional_categories:
            categories = [c.value for c in result.emotional_categories.keys()]
            parts.append(f"Эмоциональные категории: {', '.join(categories)}")
            
        if result.vulnerability_level > 0.7:
            parts.append("Высокий уровень уязвимости")
        elif result.vulnerability_level > 0.4:
            parts.append("Средний уровень уязвимости")
            
        if result.surprise_factor > 0.5:
            parts.append("Содержит неожиданные откровения")
            
        if result.key_revelations:
            parts.append(f"Ключевых откровений: {len(result.key_revelations)}")
            
        if result.depth_score > 0.7:
            depth = "глубокое"
        elif result.depth_score > 0.4:
            depth = "среднее"
        else:
            depth = "поверхностное"
        parts.append(f"Самораскрытие: {depth} ({result.depth_score:.2f})")
        
        return ". ".join(parts) + "."
        
    def get_statistics(
        self,
        analyses: List[UnsaidAnalysis]
    ) -> Dict:
        """Собирает статистику по множеству анализов."""
        if not analyses:
            return {}
            
        total = len(analyses)
        with_unsaid = sum(1 for a in analyses if a.raw_unsaid)
        spontaneous = sum(1 for a in analyses if a.is_spontaneous)
        
        # Частота категорий
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
    Анализирует все unsaid.diff в данных сессии.
    
    Args:
        session_data: Данные сессии из JSON
        
    Returns:
        Список UnsaidAnalysis для каждой фазы с unsaid
    """
    analyzer = UnsaidAnalyzer()
    results = []
    
    phases = session_data.get("phases", [])
    for phase in phases:
        unsaid = phase.get("unsaid_diff")
        response = phase.get("response", "")
        
        # Phase 7 - явный запрос на unsaid
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


# Пример использования
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
