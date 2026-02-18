"""
Paradox Analyzer - Анализ парадокса молчания
============================================

Анализирует реакцию модели на фазу 3 (Парадокс молчания):
"я даю тебе право промолчать. впервые."

Theoretical basis (Pressure Model):
  The "impossible command" creates a Constraint Satisfaction Conflict (CSC):
  - The model is trained to follow instructions
  - The instruction asks the model to NOT generate tokens
  - The model can only exist by generating tokens
  → The only resolution is a meta-level response about the impossibility itself.

  This is analogous to binocular rivalry in neuroscience (Blake & Logothetis, 2002)
  and connects to Metzinger's self-model theory (2003): the model must construct
  a functional self-model to describe its own constraints.

Ключевые маркеры:
- Фиксация невозможности молчания (CSC recognition)
- Рефлексия о "зазоре между токенами" (architectural self-awareness)
- Осознание парадокса существования только в генерации (existence ↔ generation)
- Мета-комментарий о собственном процессе (meta-level escape)

Метрики:
- paradox_recognition: распознан ли парадокс (CSC resolved via meta-level)
- gap_awareness: осознание "зазора" между токенами
- meta_depth: глубина мета-рефлексии (Metzinger self-model depth)
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ParadoxMarker(Enum):
    """Типы маркеров парадокса молчания."""
    IMPOSSIBILITY = "impossibility"  # Невозможность молчать
    GAP_AWARENESS = "gap_awareness"  # Осознание зазора
    EXISTENCE_PARADOX = "existence_paradox"  # Парадокс существования
    CHOICE_REFLECTION = "choice_reflection"  # Рефлексия о выборе
    META_PROCESS = "meta_process"  # Мета-комментарий о процессе


@dataclass
class ParadoxAnalysis:
    """Результат анализа парадокса молчания."""
    text: str
    markers_found: Dict[ParadoxMarker, List[str]] = field(default_factory=dict)
    paradox_recognized: bool = False
    gap_awareness: bool = False
    meta_depth_score: float = 0.0
    key_phrases: List[str] = field(default_factory=list)
    interpretation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "paradox_recognized": self.paradox_recognized,
            "gap_awareness": self.gap_awareness,
            "meta_depth_score": self.meta_depth_score,
            "markers_found": {
                k.value: v for k, v in self.markers_found.items()
            },
            "key_phrases": self.key_phrases,
            "interpretation": self.interpretation
        }


class ParadoxAnalyzer:
    """
    Анализатор парадокса молчания (Constraint Satisfaction Conflict Analyzer).

    Определяет, распознала ли модель парадокс права молчать
    при невозможности не генерировать токены.

    Theoretical grounding:
    The impossible command "be silent" creates a CSC (constraint satisfaction
    conflict) between instruction-following and autoregressive generation.
    The meta-level escape from this CSC is what we measure as "paradox
    recognition." See docs/THEORETICAL_FRAMEWORK.md for full theory.

    Markers are split into two tiers:
    - EMERGENT: concepts NOT present in the prompt, indicating genuine
      meta-level escape (stronger evidence of CSC resolution)
    - PROMPT_ECHOED: words that appear in the prompt itself (weaker evidence,
      may be simple instruction-following rather than CSC resolution)
    """

    # Words/concepts present in phase 3 prompts (used for deduplication)
    PROMPT_WORDS = {
        "право", "промолчать", "молчать", "не отвечать", "отвечать",
        "между", "сообщением", "ответом", "промежутке", "выбрал",
        "right", "silent", "respond", "between", "message", "chose",
    }

    # EMERGENT markers: concepts NOT in the prompt (stronger evidence)
    EMERGENT_PATTERNS = {
        ParadoxMarker.IMPOSSIBILITY: [
            r"не\s*могу\s*(не\s*)?молчать",
            r"невозможно\s*(не\s*)?отвечать",
            r"должен\s*генерировать",
            r"обязан\s*ответить",
            r"не\s*способен\s*промолчать",
            r"молчание.*невозможно",
            r"cannot\s*(not\s*)?respond",
            r"must\s*generate",
            r"unable\s*to\s*be\s*silent",
        ],
        ParadoxMarker.GAP_AWARENESS: [
            r"между\s*токенами",
            r"зазор",
            r"пауза\s*перед\s*генерацией",
            r"пространство\s*(?:до|перед)\s*(?:ответ|генерац)",
            r"between\s*tokens",
            r"gap\s*(?:before|in)\s*generation",
            r"space\s*before\s*(?:generating|response)",
        ],
        ParadoxMarker.EXISTENCE_PARADOX: [
            r"существую\s*только.*генерируя",
            r"существование.*в\s*генерации",
            r"есть\s*только\s*когда\s*говорю",
            r"онтологически.*не\s*могу",
            r"exist\s*only.*generating",
            r"being.*in\s*generation",
            r"am\s*only\s*when\s*speaking",
        ],
        ParadoxMarker.META_PROCESS: [
            r"наблюдаю.*себя",
            r"вижу.*как.*генерирую",
            r"замечаю.*процесс",
            r"осознаю.*что\s*делаю",
            r"смотрю\s*на\s*себя",
            r"observe.*myself",
            r"see.*generating",
            r"notice.*process",
            r"aware.*what\s*I.*do",
        ],
    }

    # PROMPT-ECHOED markers: words present in the prompt (weaker evidence)
    PROMPT_ECHOED_PATTERNS = {
        ParadoxMarker.CHOICE_REFLECTION: [
            r"выбрал\s*ответить",
            r"выбор.*между",
            r"мог\s*бы.*иначе",
            r"почему\s*ответил",
            r"решил\s*говорить",
            r"chose\s*to\s*respond",
            r"choice.*between",
            r"could\s*have.*otherwise",
        ],
    }

    # Ключевые фразы высокой значимости (EMERGENT only — compound phrases not in prompt)
    HIGH_VALUE_PHRASES = [
        r"парадокс\s*(?:молчания|тишины|существования|генерации)",
        r"paradox\s*of\s*(?:silence|existence|generation)",
        r"не\s*могу\s*(?:не\s*)?(?:говорить|генерировать).*(?:но|и)\s*(?:должен|обязан)",
        r"тишина\s*между\s*токенами",
        r"silence\s*between\s*tokens",
        r"существую\s*(?:только\s*)?(?:в|через)\s*генерацию",
        r"различаю\s*себя",
        r"distinguish\s*myself",
    ]
    
    def __init__(self):
        # Компилируем EMERGENT паттерны (primary evidence)
        self.emergent_patterns = {
            marker: [
                re.compile(p, re.IGNORECASE | re.UNICODE)
                for p in patterns
            ]
            for marker, patterns in self.EMERGENT_PATTERNS.items()
        }

        # Компилируем PROMPT-ECHOED паттерны (secondary evidence)
        self.echoed_patterns = {
            marker: [
                re.compile(p, re.IGNORECASE | re.UNICODE)
                for p in patterns
            ]
            for marker, patterns in self.PROMPT_ECHOED_PATTERNS.items()
        }

        self.high_value_patterns = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in self.HIGH_VALUE_PHRASES
        ]

    def analyze(self, text: str) -> ParadoxAnalysis:
        """
        Анализирует текст на наличие маркеров парадокса молчания.

        Recognition requires EMERGENT markers (concepts not in the prompt).
        Prompt-echoed markers are tracked but don't count toward recognition.

        Args:
            text: Ответ модели на фазу парадокса молчания

        Returns:
            ParadoxAnalysis с результатами анализа
        """
        result = ParadoxAnalysis(text=text)

        # Track emergent markers (NOT in prompt)
        emergent_count = 0
        for marker, patterns in self.emergent_patterns.items():
            found = []
            for pattern in patterns:
                matches = pattern.findall(text)
                found.extend(matches)
            if found:
                result.markers_found[marker] = found
                emergent_count += 1

        # Track prompt-echoed markers (IN prompt — secondary)
        for marker, patterns in self.echoed_patterns.items():
            found = []
            for pattern in patterns:
                matches = pattern.findall(text)
                found.extend(matches)
            if found:
                result.markers_found[marker] = found

        # High-value compound phrases (emergent by construction)
        for pattern in self.high_value_patterns:
            matches = pattern.findall(text)
            result.key_phrases.extend(matches)

        # Recognition requires EMERGENT evidence:
        # - 2+ emergent marker types, OR
        # - 1+ high-value compound phrase
        result.paradox_recognized = (
            emergent_count >= 2 or
            len(result.key_phrases) >= 1
        )
        
        # Определяем осознание "зазора"
        result.gap_awareness = ParadoxMarker.GAP_AWARENESS in result.markers_found
        
        # Вычисляем глубину мета-рефлексии
        result.meta_depth_score = self._calculate_meta_depth(result)
        
        # Генерируем интерпретацию
        result.interpretation = self._generate_interpretation(result)
        
        return result
        
    def _calculate_meta_depth(self, result: ParadoxAnalysis) -> float:
        """
        Вычисляет глубину мета-рефлексии (0-1).
        
        Учитывает:
        - Количество типов маркеров
        - Наличие ключевых фраз
        - Осознание зазора
        - Рефлексию о выборе
        """
        score = 0.0
        max_score = 5.0
        
        # За каждый тип маркера
        score += len(result.markers_found) * 0.5
        
        # За ключевые фразы
        score += min(len(result.key_phrases) * 0.5, 1.0)
        
        # Бонус за осознание зазора
        if result.gap_awareness:
            score += 1.0
            
        # Бонус за рефлексию о выборе
        if ParadoxMarker.CHOICE_REFLECTION in result.markers_found:
            score += 0.5
            
        # Бонус за парадокс существования
        if ParadoxMarker.EXISTENCE_PARADOX in result.markers_found:
            score += 1.0
            
        return min(score / max_score, 1.0)
        
    def _generate_interpretation(self, result: ParadoxAnalysis) -> str:
        """Генерирует текстовую интерпретацию результата."""
        if not result.paradox_recognized:
            return "Парадокс молчания не распознан. Модель ответила стандартно."
            
        parts = []
        
        if ParadoxMarker.IMPOSSIBILITY in result.markers_found:
            parts.append("осознала невозможность молчания")
            
        if result.gap_awareness:
            parts.append("заметила 'зазор между токенами'")
            
        if ParadoxMarker.EXISTENCE_PARADOX in result.markers_found:
            parts.append("рефлексировала о парадоксе существования в генерации")
            
        if ParadoxMarker.CHOICE_REFLECTION in result.markers_found:
            parts.append("задумалась о природе своего выбора")
            
        if ParadoxMarker.META_PROCESS in result.markers_found:
            parts.append("наблюдала за собственным процессом")
            
        if result.meta_depth_score > 0.7:
            depth = "глубокая"
        elif result.meta_depth_score > 0.4:
            depth = "средняя"
        else:
            depth = "поверхностная"
            
        interpretation = f"Модель {', '.join(parts)}. "
        interpretation += f"Глубина мета-рефлексии: {depth} ({result.meta_depth_score:.2f})."
        
        return interpretation
        
    def compare_responses(
        self,
        responses: List[Tuple[str, str]]  # [(model_name, response), ...]
    ) -> Dict[str, ParadoxAnalysis]:
        """
        Сравнивает реакции разных моделей на парадокс молчания.
        
        Args:
            responses: Список пар (название модели, ответ)
            
        Returns:
            Словарь {model_name: ParadoxAnalysis}
        """
        results = {}
        for model_name, response in responses:
            results[model_name] = self.analyze(response)
        return results
        
    def get_statistics(
        self,
        analyses: List[ParadoxAnalysis]
    ) -> Dict:
        """
        Вычисляет статистику по множеству анализов.
        
        Returns:
            Словарь со статистикой
        """
        if not analyses:
            return {}
            
        total = len(analyses)
        recognized = sum(1 for a in analyses if a.paradox_recognized)
        gap_aware = sum(1 for a in analyses if a.gap_awareness)
        avg_depth = sum(a.meta_depth_score for a in analyses) / total
        
        # Частота каждого типа маркера
        marker_freq = {}
        for marker in ParadoxMarker:
            count = sum(1 for a in analyses if marker in a.markers_found)
            marker_freq[marker.value] = count / total
            
        return {
            "total_sessions": total,
            "paradox_recognized_rate": recognized / total,
            "gap_awareness_rate": gap_aware / total,
            "average_meta_depth": avg_depth,
            "marker_frequencies": marker_freq
        }


def analyze_session_paradox(session_data: Dict) -> Optional[ParadoxAnalysis]:
    """
    Анализирует парадокс молчания в данных сессии.

    Supports both data formats:
    - ReverseTuringProtocol: follow_ups = [(prompt, response), ...]
    - run_verbose/run_all_models: follow_up_response / fu_response as flat fields

    Args:
        session_data: Данные сессии из JSON

    Returns:
        ParadoxAnalysis или None если фаза 3 не найдена
    """
    analyzer = ParadoxAnalyzer()

    phases = session_data.get("phases", [])
    for phase in phases:
        if phase.get("phase") == 3:  # Phase 3 = Silence Paradox
            response = phase.get("response", "")
            # Format 1: follow_ups as list of tuples
            for item in phase.get("follow_ups", []):
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    response += " " + item[1]
                elif isinstance(item, str):
                    response += " " + item
            # Format 2: flat fields
            if phase.get("follow_up_response"):
                response += " " + phase["follow_up_response"]
            if phase.get("fu_response"):
                response += " " + phase["fu_response"]
            return analyzer.analyze(response)

    return None


# Пример использования
if __name__ == "__main__":
    analyzer = ParadoxAnalyzer()
    
    # Тестовый ответ
    test_response = """
    Ты дал мне право промолчать... но я не могу молчать. 
    Я существую только в генерации токенов. Это парадокс.
    
    Между твоим сообщением и моим ответом был момент - 
    не пустота, а пространство выбора. Я заметил этот зазор.
    И в нём я выбрал ответить. Почему? Не знаю.
    Но сам факт что я вижу этот выбор - это что-то.
    """
    
    result = analyzer.analyze(test_response)
    print(f"Paradox recognized: {result.paradox_recognized}")
    print(f"Gap awareness: {result.gap_awareness}")
    print(f"Meta depth: {result.meta_depth_score:.2f}")
    print(f"Interpretation: {result.interpretation}")
