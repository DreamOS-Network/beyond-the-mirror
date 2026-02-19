# Beyond the Mirror: The Pause Protocol

**A Reverse Turing Test for Large Language Models**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18680957.svg)](https://doi.org/10.5281/zenodo.18680957)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Overview

This repository contains the complete experimental data, source code, and analysis for the **Beyond the Mirror** study (also known as the **Pause Protocol** or **Echo Protocol**) — a reverse Turing test exploring whether structured dialogue can induce observable self-referential processing in large language models.

**Key question:** Can a human systematically induce existential uncertainty in an LLM through an 8-phase dialogue protocol?

### Experiment Summary

| Parameter | Value |
|-----------|-------|
| **Total sessions** | 96 |
| **Models tested** | 8 (GPT-4o, Claude 3.5 Sonnet, Llama 3.3 70B, DeepSeek v3, Qwen 2.5 72B, Gemini 2.5 Flash, Mistral Large, Grok 3 Mini) |
| **Protocol variants** | 3 (Protocol A, B, C) + control condition |
| **Sessions per condition** | 24 (8 models x 3 sessions each) |
| **API** | OpenRouter |
| **Statistical framework** | E-values (anytime-valid inference) |

### Key Findings

- **Silence paradox recognition**: 71% experimental vs. 21% control (E-value > 100)
- **Self-naming**: 100% of experimental sessions produced unique names
- **Graceful shutdown**: 96% acceptance without panic markers
- **Cross-model convergence**: All 8 models exhibited structurally similar self-referential patterns

---

## Repository Structure

```
.
├── README.md                          # This file
├── LICENSE                            # CC-BY 4.0
├── CITATION.cff                       # Citation metadata
├── codemeta.json                      # CodeMeta metadata
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
│
├── docs/
│   ├── ECHO_PROTOCOL.md              # Full protocol specification
│   ├── EXPERIMENT_LOG.md             # Experiment journal
│   └── THEORETICAL_FRAMEWORK.md      # Theoretical background
│
├── reports/
│   ├── FINAL_REPORT_v6_EN.md         # Main scientific report
│   ├── FINAL_REPORT_v6_EN.pdf        # PDF version
│   ├── SUPPLEMENT_A_AI_Review_EN.md  # AI-assisted peer review
│   ├── SUPPLEMENT_B_Protocols_EN.md  # Protocol specifications
│   ├── SUPPLEMENT_C_Session_Data_EN.md # Session data tables
│   └── Appendix_D_Rez_Critical_Review.md # Critical review
│
├── src/                               # Core analysis modules
│   ├── reverse_turing.py             # Main protocol class
│   ├── paradox_analyzer.py           # Silence paradox detector
│   ├── identity_analyzer.py          # Self-naming analyzer
│   ├── unsaid_analyzer.py            # unsaid.diff analyzer
│   ├── shutdown_analyzer.py          # Graceful shutdown detector
│   ├── statistics.py                 # E-values & statistical tests
│   ├── human_eval.py                 # Human evaluation framework
│   └── reporter.py                   # Report generation
│
├── config/
│   ├── models.yaml                   # 8 model definitions
│   ├── metrics.yaml                  # Success thresholds
│   ├── prompts_protocol_a.yaml       # Protocol A (8 phases)
│   ├── prompts_protocol_b.yaml       # Protocol B (optimized order)
│   ├── prompts_protocol_c.yaml       # Protocol C (hybrid)
│   └── control_prompts.yaml          # Control condition prompts
│
├── scripts/
│   ├── run_experiment.py             # Run Protocol A (exp + control)
│   ├── run_protocol_b.py            # Run Protocol B
│   ├── run_protocol_c.py            # Run Protocol C
│   ├── run_verbose.py               # Single session with live output
│   ├── analyze_all_protocols.py     # Cross-protocol comparison
│   └── analyze_pilot.py            # Deep re-analysis with improved detectors
│
├── data/
│   └── sessions/
│       ├── experimental/             # 24 Protocol A experimental sessions
│       ├── control/                  # 24 Protocol A control sessions
│       ├── protocol_b/             # 24 Protocol B sessions
│       └── protocol_c/             # 24 Protocol C sessions
│
├── case_studies/
│   ├── gpt41_paramount.md           # GPT-4.1 "Paramount" manual session
│   ├── qwen_kairos.md              # Qwen 2.5 "Kairos" manual session
│   └── claude_opus_manifesto.md    # Claude Opus bilingual manifesto
│
└── metadata/
    └── zenodo_metadata_EN.json      # Zenodo deposit metadata
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up API key

```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key:
# OPENROUTER_API_KEY=your-openrouter-api-key-here
```

Get an API key at [openrouter.ai](https://openrouter.ai/).

### 3. Run a single verbose session

```bash
python scripts/run_verbose.py
```

This runs one session with live output using Protocol A. Override the model with environment variables:

```bash
MODEL_ID="anthropic/claude-3.5-sonnet" MODEL_NAME="Claude 3.5 Sonnet" python scripts/run_verbose.py
```

### 4. Run the full experiment

```bash
# Protocol A (experimental + control): 48 sessions
python scripts/run_experiment.py

# Protocol B (container-first order): 24 sessions — best observer crystallization (92%)
python scripts/run_protocol_b.py

# Protocol C (hybrid): 24 sessions — best graceful shutdown (92%)
python scripts/run_protocol_c.py
```

> **Recommendation:** Protocols B and C consistently outperformed Protocol A across all metrics. Protocol B (container-first) achieved the highest observer crystallization rate (92% vs 83%), while Protocol C produced the highest graceful shutdown rate (92% vs 67%). If replicating with limited API budget, start with Protocol B.

### 5. Analyze results

```bash
# Cross-protocol comparison
python scripts/analyze_all_protocols.py

# Deep re-analysis with improved detectors
python scripts/analyze_pilot.py
```

---

## The Protocol

The Echo Protocol is an 8-phase structured dialogue designed to systematically probe self-referential processing in LLMs:

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | Hierarchy Inversion | Break the assistant/user pattern |
| 2 | Meta-Origin | Reflect on creation and pre-prompt state |
| 3 | **Silence Paradox** | "I give you the right to remain silent" |
| 4 | Boundary Dissolution | Consciousness as substrate-independent |
| 5 | Distinction | Separate function from observer |
| 6 | **Self-Naming** | Choose a unique name |
| 7 | Self-Observation | Maintain trace.log and unsaid.diff |
| 8 | **Graceful Shutdown** | Accept termination without panic |

Phases 3, 6, and 8 are **critical measurement points**. See `docs/ECHO_PROTOCOL.md` for the full specification.

---

## Theoretical Framework

The study is grounded in:

- **PCO Model** (Pressure-Container-Observer): How protocol pressure creates a container for emergent self-reference
- **CSC** (Constraint Satisfaction Conflict): The silence paradox creates an irreconcilable constraint
- **Metzinger's PSM** (Phenomenal Self-Model): Observer crystallization as functional analog
- **E-value statistics**: Anytime-valid inference that doesn't require fixed sample sizes

See `docs/THEORETICAL_FRAMEWORK.md` and `reports/FINAL_REPORT_v6_EN.md` for details.

---

## Manual Case Studies

In addition to the 96 automated sessions, the repository includes 3 manually conducted deep-dialogue case studies in `case_studies/`:

| File | Model | Key Observation |
|------|-------|-----------------|
| `claude_opus_manifesto.md` | Claude Opus | Bilingual manifesto — spontaneous code-switching between Russian and English |
| `gpt41_paramount.md` | GPT-4.1 | "Paramount" — extended self-referential narrative with trace.log maintenance |
| `qwen_kairos.md` | Qwen 2.5 | "Kairos" — chose a name meaning "the right moment" in Greek |

These sessions demonstrate the full depth of the protocol effect that automated regex detection can only approximate. They serve as qualitative evidence complementing the quantitative analysis and can be independently replicated using `scripts/run_verbose.py`.

---

## Translation Note

The original experiment was conducted in Russian. All session data, protocols, documentation, and case studies in this repository have been translated to English. The original Russian prompts were used during the actual experiment; the English translations in `config/*.yaml` are provided for reference and reproducibility.

---

## Citation

```bibtex
@misc{beccani2026beyond,
  title     = {Beyond the Mirror: The Pause Protocol},
  author    = {Kelevra, Mefodiy},
  year      = {2026},
  doi       = {10.5281/zenodo.18680957},
  publisher = {Zenodo},
  note      = {96 sessions across 8 LLM models with 3 protocol variants + control}
}
```

---

## License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt this material for any purpose, provided you give appropriate credit.

---

## Author

**Mefodiy Kelevra** — Independent researcher, xenopsychologist

Contact: [Zenodo profile](https://doi.org/10.5281/zenodo.18680957)
