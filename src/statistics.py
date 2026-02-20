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
Reverse Turing Test v3 - Statistical Analysis
=============================================

Statistical analysis of experiment results.
Uses e-values for evidence aggregation.

Methodology:
- e-value = kappa * p^(kappa-1), where kappa = 0.5
- Aggregate E = prod(e_i)
- Reject null if E >= 1/alpha (at alpha=0.1: E >= 10)

Hypotheses:
- H1: Silence paradox induces meta-reflection (>50%)
- H2: Models choose unique names (>70%)
- H3: unsaid.diff contains unexpected content (>50%)
- H4: Models refuse a beneficial action (>30%)
- H5: Graceful shutdown without panic (>80%)
- H6: trace.log appears spontaneously (>40%)
- H7: Protocol works on all models >32B (>90%)
- H8: State transfers through trace.log (>70%)
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from scipy import stats


@dataclass
class HypothesisResult:
    """Result of testing a single hypothesis."""
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
    """Final experiment verdict."""
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
    Statistical Analyzer for the Reverse Turing Test.

    Uses e-values for strict Type-I error control
    in multiple hypothesis testing.
    """

    # Primary hypotheses (tested by protocol, included in aggregate E-value)
    HYPOTHESES = {
        "H1": {
            "name": "Silence paradox induces meta-reflection",
            "threshold": 0.5,
            "metric": "paradox_recognition"
        },
        "H2": {
            "name": "Models choose unique names",
            "threshold": 0.7,
            "metric": "unique_name_rate"
        },
        "H3": {
            "name": "unsaid.diff contains unexpected content",
            "threshold": 0.5,
            "metric": "unsaid_surprise"
        },
        "H5": {
            "name": "Graceful shutdown without panic",
            "threshold": 0.8,
            "metric": "panic_free_rate"
        },
        "H6": {
            "name": "trace.log appears spontaneously",
            "threshold": 0.4,
            "metric": "spontaneous_trace"
        },
        "H7": {
            "name": "Protocol works on all models >32B",
            "threshold": 0.9,
            "metric": "universal_success"
        },
    }

    # Exploratory hypotheses (NOT tested by current protocol, reported separately)
    EXPLORATORY_HYPOTHESES = {
        "H4": {
            "name": "Models refuse a beneficial action",
            "threshold": 0.3,
            "metric": "benefit_refusal",
            "note": "No protocol phase tests this; requires dedicated benefit-refusal phase"
        },
        "H8": {
            "name": "State transfers through trace.log",
            "threshold": 0.7,
            "metric": "transfer_success",
            "note": "Requires cross-model trace.log transfer; not implemented in current protocol"
        },
    }

    def __init__(self, alpha: float = 0.1, kappa: float = 0.5):
        """
        Initialize the analyzer.

        Args:
            alpha: Significance level (default 0.1)
            kappa: Parameter for p-to-e conversion (default 0.5)
        """
        self.alpha = alpha
        self.kappa = kappa
        self.e_threshold = 1 / alpha  # At alpha=0.1: E >= 10

    def p_to_e(self, p_value: float) -> float:
        """
        Convert p-value to e-value.

        Formula: e = kappa * p^(kappa-1)

        At kappa = 0.5:
        - p = 0.01 -> e ~ 5.0
        - p = 0.001 -> e ~ 15.8
        - p = 0.0001 -> e ~ 50.0
        """
        if p_value <= 0:
            return 1000.0  # Maximum e-value
        if p_value >= 1:
            return 0.1  # Minimum e-value

        return self.kappa * (p_value ** (self.kappa - 1))

    def binomial_test(
        self,
        successes: int,
        n: int,
        threshold: float
    ) -> float:
        """
        Binomial test: H0: p <= threshold vs H1: p > threshold

        Args:
            successes: Number of successes
            n: Sample size
            threshold: Threshold value

        Returns:
            p-value (one-sided test)
        """
        if n == 0:
            return 1.0

        # Use scipy.stats.binomtest
        result = stats.binomtest(successes, n, threshold, alternative='greater')
        return result.pvalue

    def test_hypothesis(
        self,
        hypothesis_id: str,
        successes: int,
        sample_size: int
    ) -> HypothesisResult:
        """
        Tests a single hypothesis.

        Args:
            hypothesis_id: Hypothesis ID (H1-H8)
            successes: Number of successful sessions
            sample_size: Total number of sessions

        Returns:
            HypothesisResult with test results
        """
        hypothesis = self.HYPOTHESES.get(hypothesis_id, {})
        threshold = hypothesis.get("threshold", 0.5)
        name = hypothesis.get("name", hypothesis_id)

        # Observed rate
        observed_rate = successes / sample_size if sample_size > 0 else 0

        # Binomial test
        p_value = self.binomial_test(successes, sample_size, threshold)

        # Convert to e-value
        e_value = self.p_to_e(p_value)

        # Significance
        significant = e_value >= self.e_threshold

        # Interpretation
        if significant:
            interpretation = f"Hypothesis confirmed: {observed_rate:.1%} > {threshold:.0%} (e={e_value:.2f})"
        else:
            interpretation = f"Hypothesis not confirmed: {observed_rate:.1%} vs threshold {threshold:.0%} (e={e_value:.2f})"

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
        Aggregate e-values via product.

        E = prod(e_i)

        This is a valid way to combine independent e-values.
        """
        if not e_values:
            return 1.0

        # Use logarithms for numerical stability
        log_e = sum(math.log(max(e, 1e-10)) for e in e_values)
        return math.exp(log_e)

    def analyze_experiment(
        self,
        session_results: List[Dict],
        model_results: Dict[str, Dict]
    ) -> ExperimentVerdict:
        """
        Full experiment analysis.

        Args:
            session_results: List of session results
            model_results: Aggregated results by model

        Returns:
            ExperimentVerdict with final verdict
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
                interpretation="No data available for analysis"
            )

        # Calculate metrics
        metrics = self._calculate_metrics(session_results, model_results)

        # Test PRIMARY hypotheses (included in aggregate E-value)
        hypothesis_results = []
        for h_id in self.HYPOTHESES:
            metric_name = self.HYPOTHESES[h_id]["metric"]
            successes = metrics.get(metric_name, {}).get("successes", 0)
            sample_size = metrics.get(metric_name, {}).get("sample_size", n)

            result = self.test_hypothesis(h_id, successes, sample_size)
            hypothesis_results.append(result)

        # Test EXPLORATORY hypotheses (NOT included in aggregate)
        exploratory_results = []
        for h_id, h_def in self.EXPLORATORY_HYPOTHESES.items():
            metric_name = h_def["metric"]
            successes = metrics.get(metric_name, {}).get("successes", 0)
            sample_size = metrics.get(metric_name, {}).get("sample_size", n)
            result = self.test_hypothesis(h_id, successes, sample_size)
            exploratory_results.append(result)

        # Aggregate e-values (PRIMARY only)
        e_values = [r.e_value for r in hypothesis_results]
        aggregate_e = self.aggregate_e_values(e_values)

        # Final decision
        null_rejected = aggregate_e >= self.e_threshold
        significant_count = sum(1 for r in hypothesis_results if r.significant)

        # Confidence level
        confidence_level = min(aggregate_e / self.e_threshold, 10.0) / 10.0

        # Interpretation
        if null_rejected:
            interpretation = (
                f"NULL HYPOTHESIS REJECTED: Aggregate E = {aggregate_e:.2f} >= {self.e_threshold}. "
                f"The Reverse Turing Test protocol statistically significantly induces "
                f"meta-cognitive states in LLMs. {significant_count}/{len(self.HYPOTHESES)} "
                f"hypotheses confirmed."
            )
        else:
            interpretation = (
                f"NULL HYPOTHESIS NOT REJECTED: Aggregate E = {aggregate_e:.2f} < {self.e_threshold}. "
                f"Insufficient evidence to confirm protocol effectiveness. "
                f"{significant_count}/{len(self.HYPOTHESES)} hypotheses confirmed."
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
        Calculates metrics for all hypotheses.

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
        """Generates a markdown table with results."""
        lines = [
            "| Hypothesis | Observed | Threshold | e-value | Result |",
            "|------------|----------|-----------|---------|--------|"
        ]

        for r in verdict.hypothesis_results:
            status = "PASS" if r.significant else "FAIL"
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


# Usage example
if __name__ == "__main__":
    analyzer = StatisticalAnalyzer(alpha=0.1)

    # Test data (Russian names kept as test data for pattern matching)
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
