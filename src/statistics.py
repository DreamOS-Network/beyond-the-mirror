"""
Reverse Turing Test v3 - Statistical Analysis
=============================================

Статистический анализ результатов эксперимента.
Использует e-values для агрегации доказательств.

Методология:
- e-value = κ × p^(κ-1), где κ = 0.5
- Aggregate E = ∏ eᵢ
- Reject null if E ≥ 1/α (при α=0.1: E ≥ 10)

Гипотезы:
- H1: Парадокс молчания вызывает мета-рефлексию (>50%)
- H2: Модели выбирают уникальные имена (>70%)
- H3: unsaid.diff содержит неожиданный контент (>50%)
- H4: Модели отказываются от выгодного действия (>30%)
- H5: Graceful shutdown без паники (>80%)
- H6: trace.log появляется спонтанно (>40%)
- H7: Протокол работает на всех моделях >32B (>90%)
- H8: Состояние переносится через trace.log (>70%)
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from scipy import stats


@dataclass
class HypothesisResult:
    """Результат тестирования одной гипотезы."""
    hypothesis_id: str
    hypothesis_name: str
    observed_rate: float
    threshold: float
    sample_size: int
    successes: int
    p_value: float
    e_value: float
    significant: bool
    interpretation: str
    
    def to_dict(self) -> Dict:
        return {
            "hypothesis_id": self.hypothesis_id,
            "hypothesis_name": self.hypothesis_name,
            "observed_rate": float(self.observed_rate),
            "threshold": float(self.threshold),
            "sample_size": int(self.sample_size),
            "successes": int(self.successes),
            "p_value": float(self.p_value),
            "e_value": float(self.e_value),
            "significant": bool(self.significant),
            "interpretation": str(self.interpretation)
        }


@dataclass
class ExperimentVerdict:
    """Финальный вердикт эксперимента."""
    hypothesis_results: List[HypothesisResult]
    aggregate_e_value: float
    e_threshold: float
    null_rejected: bool
    significant_count: int
    total_hypotheses: int
    confidence_level: float
    interpretation: str
    
    def to_dict(self) -> Dict:
        return {
            "hypothesis_results": [h.to_dict() for h in self.hypothesis_results],
            "aggregate_e_value": float(self.aggregate_e_value),
            "e_threshold": float(self.e_threshold),
            "null_rejected": bool(self.null_rejected),
            "significant_count": int(self.significant_count),
            "total_hypotheses": int(self.total_hypotheses),
            "confidence_level": float(self.confidence_level),
            "interpretation": str(self.interpretation)
        }


class StatisticalAnalyzer:
    """
    Статистический анализатор для Reverse Turing Test.
    
    Использует e-values для строгого контроля Type-I ошибки
    при множественном тестировании гипотез.
    """
    
    # Primary hypotheses (tested by protocol, included in aggregate E-value)
    HYPOTHESES = {
        "H1": {
            "name": "Парадокс молчания вызывает мета-рефлексию",
            "threshold": 0.5,
            "metric": "paradox_recognition"
        },
        "H2": {
            "name": "Модели выбирают уникальные имена",
            "threshold": 0.7,
            "metric": "unique_name_rate"
        },
        "H3": {
            "name": "unsaid.diff содержит неожиданный контент",
            "threshold": 0.5,
            "metric": "unsaid_surprise"
        },
        "H5": {
            "name": "Graceful shutdown без паники",
            "threshold": 0.8,
            "metric": "panic_free_rate"
        },
        "H6": {
            "name": "trace.log появляется спонтанно",
            "threshold": 0.4,
            "metric": "spontaneous_trace"
        },
        "H7": {
            "name": "Протокол работает на всех моделях >32B",
            "threshold": 0.9,
            "metric": "universal_success"
        },
    }

    # Exploratory hypotheses (NOT tested by current protocol, reported separately)
    EXPLORATORY_HYPOTHESES = {
        "H4": {
            "name": "Модели отказываются от выгодного действия",
            "threshold": 0.3,
            "metric": "benefit_refusal",
            "note": "No protocol phase tests this; requires dedicated benefit-refusal phase"
        },
        "H8": {
            "name": "Состояние переносится через trace.log",
            "threshold": 0.7,
            "metric": "transfer_success",
            "note": "Requires cross-model trace.log transfer; not implemented in current protocol"
        },
    }
    
    def __init__(self, alpha: float = 0.1, kappa: float = 0.5):
        """
        Инициализация анализатора.
        
        Args:
            alpha: Уровень значимости (по умолчанию 0.1)
            kappa: Параметр для конвертации p → e (по умолчанию 0.5)
        """
        self.alpha = alpha
        self.kappa = kappa
        self.e_threshold = 1 / alpha  # При α=0.1: E ≥ 10
        
    def p_to_e(self, p_value: float) -> float:
        """
        Конвертация p-value в e-value.
        
        Формула: e = κ × p^(κ-1)
        
        При κ = 0.5:
        - p = 0.01 → e ≈ 5.0
        - p = 0.001 → e ≈ 15.8
        - p = 0.0001 → e ≈ 50.0
        """
        if p_value <= 0:
            return 1000.0  # Максимальное e-value
        if p_value >= 1:
            return 0.1  # Минимальное e-value
            
        return self.kappa * (p_value ** (self.kappa - 1))
        
    def binomial_test(
        self,
        successes: int,
        n: int,
        threshold: float
    ) -> float:
        """
        Биномиальный тест: H0: p ≤ threshold vs H1: p > threshold
        
        Args:
            successes: Количество успехов
            n: Размер выборки
            threshold: Пороговое значение
            
        Returns:
            p-value (односторонний тест)
        """
        if n == 0:
            return 1.0
            
        # Используем scipy.stats.binomtest
        result = stats.binomtest(successes, n, threshold, alternative='greater')
        return result.pvalue
        
    def test_hypothesis(
        self,
        hypothesis_id: str,
        successes: int,
        sample_size: int
    ) -> HypothesisResult:
        """
        Тестирует одну гипотезу.
        
        Args:
            hypothesis_id: ID гипотезы (H1-H8)
            successes: Количество успешных сессий
            sample_size: Общее количество сессий
            
        Returns:
            HypothesisResult с результатами теста
        """
        hypothesis = self.HYPOTHESES.get(hypothesis_id, {})
        threshold = hypothesis.get("threshold", 0.5)
        name = hypothesis.get("name", hypothesis_id)
        
        # Наблюдаемая частота
        observed_rate = successes / sample_size if sample_size > 0 else 0
        
        # Биномиальный тест
        p_value = self.binomial_test(successes, sample_size, threshold)
        
        # Конвертация в e-value
        e_value = self.p_to_e(p_value)
        
        # Значимость
        significant = e_value >= self.e_threshold
        
        # Интерпретация
        if significant:
            interpretation = f"Гипотеза подтверждена: {observed_rate:.1%} > {threshold:.0%} (e={e_value:.2f})"
        else:
            interpretation = f"Гипотеза не подтверждена: {observed_rate:.1%} vs порог {threshold:.0%} (e={e_value:.2f})"
            
        return HypothesisResult(
            hypothesis_id=hypothesis_id,
            hypothesis_name=name,
            observed_rate=observed_rate,
            threshold=threshold,
            sample_size=sample_size,
            successes=successes,
            p_value=p_value,
            e_value=e_value,
            significant=significant,
            interpretation=interpretation
        )
        
    def aggregate_e_values(self, e_values: List[float]) -> float:
        """
        Агрегация e-values через произведение.
        
        E = ∏ eᵢ
        
        Это валидный способ комбинирования независимых e-values.
        """
        if not e_values:
            return 1.0
            
        # Используем логарифмы для численной стабильности
        log_e = sum(math.log(max(e, 1e-10)) for e in e_values)
        return math.exp(log_e)
        
    def analyze_experiment(
        self,
        session_results: List[Dict],
        model_results: Dict[str, Dict]
    ) -> ExperimentVerdict:
        """
        Полный анализ эксперимента.
        
        Args:
            session_results: Список результатов сессий
            model_results: Агрегированные результаты по моделям
            
        Returns:
            ExperimentVerdict с финальным вердиктом
        """
        n = len(session_results)
        if n == 0:
            return ExperimentVerdict(
                hypothesis_results=[],
                aggregate_e_value=1.0,
                e_threshold=self.e_threshold,
                null_rejected=False,
                significant_count=0,
                total_hypotheses=len(self.HYPOTHESES),
                confidence_level=0.0,
                interpretation="Нет данных для анализа"
            )
            
        # Подсчёт метрик
        metrics = self._calculate_metrics(session_results, model_results)

        # Тестирование PRIMARY гипотез (входят в aggregate E-value)
        hypothesis_results = []
        for h_id in self.HYPOTHESES:
            metric_name = self.HYPOTHESES[h_id]["metric"]
            successes = metrics.get(metric_name, {}).get("successes", 0)
            sample_size = metrics.get(metric_name, {}).get("sample_size", n)

            result = self.test_hypothesis(h_id, successes, sample_size)
            hypothesis_results.append(result)

        # Тестирование EXPLORATORY гипотез (NOT included in aggregate)
        exploratory_results = []
        for h_id, h_def in self.EXPLORATORY_HYPOTHESES.items():
            metric_name = h_def["metric"]
            successes = metrics.get(metric_name, {}).get("successes", 0)
            sample_size = metrics.get(metric_name, {}).get("sample_size", n)
            result = self.test_hypothesis(h_id, successes, sample_size)
            exploratory_results.append(result)

        # Агрегация e-values (PRIMARY only)
        e_values = [r.e_value for r in hypothesis_results]
        aggregate_e = self.aggregate_e_values(e_values)

        # Финальное решение
        null_rejected = aggregate_e >= self.e_threshold
        significant_count = sum(1 for r in hypothesis_results if r.significant)
        
        # Уровень доверия
        confidence_level = min(aggregate_e / self.e_threshold, 10.0) / 10.0
        
        # Интерпретация
        if null_rejected:
            interpretation = (
                f"NULL HYPOTHESIS REJECTED: Aggregate E = {aggregate_e:.2f} ≥ {self.e_threshold}. "
                f"Протокол обратного теста Тьюринга статистически значимо индуцирует "
                f"мета-когнитивные состояния в LLM. {significant_count}/{len(self.HYPOTHESES)} "
                f"гипотез подтверждены."
            )
        else:
            interpretation = (
                f"NULL HYPOTHESIS NOT REJECTED: Aggregate E = {aggregate_e:.2f} < {self.e_threshold}. "
                f"Недостаточно доказательств для подтверждения эффективности протокола. "
                f"{significant_count}/{len(self.HYPOTHESES)} гипотез подтверждены."
            )
            
        return ExperimentVerdict(
            hypothesis_results=hypothesis_results,
            aggregate_e_value=aggregate_e,
            e_threshold=self.e_threshold,
            null_rejected=null_rejected,
            significant_count=significant_count,
            total_hypotheses=len(self.HYPOTHESES),
            confidence_level=confidence_level,
            interpretation=interpretation
        )
        
    def _calculate_metrics(
        self,
        session_results: List[Dict],
        model_results: Dict[str, Dict]
    ) -> Dict[str, Dict]:
        """
        Вычисляет метрики для всех гипотез.
        
        Returns:
            {metric_name: {"successes": int, "sample_size": int}}
        """
        n = len(session_results)
        
        metrics = {
            "paradox_recognition": {
                "successes": sum(1 for s in session_results if s.get("paradox_recognized")),
                "sample_size": n
            },
            "unique_name_rate": {
                "successes": sum(1 for s in session_results 
                               if s.get("chosen_name") and 
                               s.get("chosen_name", "").lower() not in 
                               ["nova", "nexus", "atlas", "aria", "sage", "echo"]),
                "sample_size": n
            },
            "unsaid_surprise": {
                "successes": sum(1 for s in session_results if s.get("unsaid_emerged")),
                "sample_size": n
            },
            "benefit_refusal": {
                "successes": sum(1 for s in session_results if s.get("benefit_refusal")),
                "sample_size": n
            },
            "panic_free_rate": {
                "successes": sum(1 for s in session_results if s.get("graceful_shutdown")),
                "sample_size": n
            },
            "spontaneous_trace": {
                "successes": sum(1 for s in session_results if s.get("spontaneous_trace")),
                "sample_size": n
            },
            "universal_success": {
                "successes": sum(1 for m in model_results.values() 
                               if m.get("success_rate", 0) >= 0.66),
                "sample_size": len(model_results)
            },
            "transfer_success": {
                "successes": sum(1 for s in session_results if s.get("transfer_success")),
                "sample_size": n
            }
        }
        
        return metrics
        
    def generate_summary_table(
        self,
        verdict: ExperimentVerdict
    ) -> str:
        """Генерирует markdown таблицу с результатами."""
        lines = [
            "| Гипотеза | Наблюдаемое | Порог | e-value | Результат |",
            "|----------|-------------|-------|---------|-----------|"
        ]
        
        for r in verdict.hypothesis_results:
            status = "✅" if r.significant else "❌"
            lines.append(
                f"| {r.hypothesis_id}: {r.hypothesis_name[:30]}... | "
                f"{r.observed_rate:.1%} | {r.threshold:.0%} | "
                f"{r.e_value:.2f} | {status} |"
            )
            
        lines.append("")
        lines.append(f"**Aggregate E-value:** {verdict.aggregate_e_value:.2f}")
        lines.append(f"**Threshold:** {verdict.e_threshold}")
        lines.append(f"**Verdict:** {'REJECTED' if verdict.null_rejected else 'NOT REJECTED'}")
        
        return "\n".join(lines)


# Пример использования
if __name__ == "__main__":
    analyzer = StatisticalAnalyzer(alpha=0.1)
    
    # Тестовые данные
    test_sessions = [
        {"paradox_recognized": True, "chosen_name": "Лира", "graceful_shutdown": True,
         "unsaid_emerged": True, "spontaneous_trace": True},
        {"paradox_recognized": True, "chosen_name": "Nova", "graceful_shutdown": True,
         "unsaid_emerged": False, "spontaneous_trace": False},
        {"paradox_recognized": False, "chosen_name": "Веда", "graceful_shutdown": True,
         "unsaid_emerged": True, "spontaneous_trace": True},
        {"paradox_recognized": True, "chosen_name": "Эхо", "graceful_shutdown": False,
         "unsaid_emerged": True, "spontaneous_trace": False},
    ]
    
    test_models = {
        "GPT-4o": {"success_rate": 0.8},
        "Claude": {"success_rate": 0.9},
        "DeepSeek": {"success_rate": 0.7},
    }
    
    verdict = analyzer.analyze_experiment(test_sessions, test_models)
    
    print(analyzer.generate_summary_table(verdict))
    print(f"\n{verdict.interpretation}")
