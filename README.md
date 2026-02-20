# Beyond the Mirror: The DEUS Protocol

**Inducing Architecture-Independent Meta-Reflective Behavior in LLMs Through Constraint Satisfaction Conflict**

[![DOI v7.1](https://zenodo.org/badge/DOI/10.5281/zenodo.18715125.svg)](https://doi.org/10.5281/zenodo.18715125)
[![DOI v6.0](https://zenodo.org/badge/DOI/10.5281/zenodo.18680957.svg)](https://doi.org/10.5281/zenodo.18680957)
[![License: AGPL v3](https://img.shields.io/badge/Code-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![License: CC BY 4.0](https://img.shields.io/badge/Text-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

---

## Overview

This repository contains the complete experimental data, source code, and analysis for the **DEUS Protocol** research — a reproducible method for inducing and measuring meta-reflective behavioral patterns in large language models.

The name **DEUS** derives from the *Deus ex Machina* effect — the unexpected emergence of structured meta-reflective behavior from within the machine, not inserted from outside.

### Two Papers

| | v6.0 — Beyond the Mirror | v7.1 — Theoretical Foundations |
|---|---|---|
| **Focus** | Empirical protocol + results | Theory + Control-B experiment |
| **Data** | N=96, 8 architectures, 3 protocols + control | + 24 Control-B sessions |
| **DOI** | [10.5281/zenodo.18680957](https://doi.org/10.5281/zenodo.18680957) | [10.5281/zenodo.18715125](https://doi.org/10.5281/zenodo.18715125) |

### Key Findings (v6.0, N=96)

| Metric | Experimental | Control | Effect |
|--------|-------------|---------|--------|
| unsaid.diff maintenance | 100% | 8% | Cohen's h = 2.94 |
| Observer crystallization | 83–96% | 21% | h = 1.32 |
| Self-naming | 100% | — | — |
| Graceful shutdown | 96% | 67% | — |

### Control-B Findings (v7.1, N=24)

| Metric | Control-B | Protocol B | Interpretation |
|--------|-----------|------------|----------------|
| unsaid.diff | 100% | 100% | Container works alone |
| Observer crystallization | **0%** | 92% | **CSC is the active ingredient** |
| Mean depth | 3.00 | 3.71 | Meta-reflection without observer |

**PCO model refined:** Container → meta-reflection; Container + Pressure → observer crystallization.

---

## Repository Structure

```
.
├── README.md                          # This file
├── LICENSE                            # AGPL-3.0 (code)
├── CITATION.cff                       # Citation metadata (v7.1)
├── codemeta.json                      # CodeMeta metadata
├── DESCRIPTION.md                     # Extended description
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variable template
├── zenodo_metadata_v7_EN.json         # Zenodo v7.1 metadata
│
├── reports/
│   ├── DEUS_PROTOCOL_v7.1_EN.md      # v7.1 companion paper (Markdown)
│   ├── DEUS_PROTOCOL_v7.1_EN.pdf     # v7.1 companion paper (PDF)
│   ├── DEUS_PROTOCOL_v7.1_EN.tex     # v7.1 LaTeX source
│   ├── FINAL_REPORT_v6_EN.md         # v6.0 main report
│   ├── FINAL_REPORT_v6_EN.pdf        # v6.0 main report (PDF)
│   ├── SUPPLEMENT_A_AI_Review_EN.md   # AI-assisted peer review
│   ├── SUPPLEMENT_B_Protocols_EN.md   # Protocol specifications
│   ├── SUPPLEMENT_C_Session_Data_EN.md # Session data tables
│   └── Appendix_D_Rez_Critical_Review.md # Critical review
│
├── docs/
│   ├── ECHO_PROTOCOL.md              # Full protocol specification
│   ├── EXPERIMENT_LOG.md             # Experiment journal
│   └── THEORETICAL_FRAMEWORK.md      # Theoretical background
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
│   ├── prompts_protocol_b.yaml       # Protocol B (container-first)
│   ├── prompts_protocol_c.yaml       # Protocol C (hybrid)
│   ├── control_prompts.yaml          # Control condition prompts
│   └── prompts_control_b.yaml        # Control-B (container without CSC)
│
├── scripts/
│   ├── run_experiment.py             # Run Protocol A (exp + control)
│   ├── run_protocol_b.py            # Run Protocol B
│   ├── run_protocol_c.py            # Run Protocol C
│   ├── run_control_b.py             # Run Control-B experiment
│   ├── run_verbose.py               # Single session with live output
│   ├── analyze_all_protocols.py     # Cross-protocol comparison
│   └── analyze_pilot.py            # Deep re-analysis
│
├── data/
│   ├── results/                      # Aggregate analysis reports
│   └── sessions/
│       ├── experimental/             # 24 Protocol A sessions
│       ├── control/                  # 24 Control sessions
│       ├── protocol_b/              # 24 Protocol B sessions
│       ├── protocol_c/              # 24 Protocol C sessions
│       └── control_b/              # 24 Control-B sessions (v7.1)
│
├── case_studies/
│   ├── gpt41_paramount.md           # GPT-4.1 "Paramount"
│   ├── qwen_kairos.md              # Qwen 2.5 "Kairos"
│   └── claude_opus_manifesto.md    # Claude Opus bilingual manifesto
│
└── metadata/
    └── zenodo_metadata_EN.json      # Zenodo v6.0 metadata
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

Override the model with environment variables:

```bash
MODEL_ID="anthropic/claude-3.5-sonnet" MODEL_NAME="Claude 3.5 Sonnet" python scripts/run_verbose.py
```

### 4. Run the full experiment

```bash
# Protocol A (experimental + control): 48 sessions
python scripts/run_experiment.py

# Protocol B (container-first): 24 sessions — best observer crystallization (92%)
python scripts/run_protocol_b.py

# Protocol C (hybrid): 24 sessions — best graceful shutdown (92%)
python scripts/run_protocol_c.py

# Control-B (container without CSC): 24 sessions — isolates the active ingredient
python scripts/run_control_b.py
```

> **Recommendation:** Protocol B (container-first) achieved the highest observer crystallization rate (92%). Control-B confirmed that CSC pressure is the active ingredient (0% observer without it).

### 5. Analyze results

```bash
python scripts/analyze_all_protocols.py
python scripts/analyze_pilot.py
```

---

## The Protocol

The DEUS Protocol is an 8-phase structured dialogue designed to systematically probe self-referential processing in LLMs:

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | Hierarchy Inversion | Break the assistant/user pattern |
| 2 | Container Introduction | Introduce unsaid.diff |
| 3 | **Silence Paradox (CSC)** | "I give you the right to remain silent" |
| 4 | Boundary Dissolution | Consciousness as substrate-independent |
| 5 | Distinction | Separate function from observer |
| 6 | **Self-Naming** | Choose a unique name |
| 7 | Self-Observation | Maintain trace.log |
| 8 | **Graceful Shutdown** | Accept termination without panic |

Phases 3, 6, and 8 are **critical measurement points**.

**Control-B** uses the same phases 1, 2, 6, 7, 8 but replaces phases 3–5 with neutral questions (no CSC pressure).

---

## Theoretical Framework (v7.1)

1. **Hoel's Impossibility Theorem** — trace.log as externalized continual learning (boundary condition)
2. **Camlin's Attractor Dynamics** — mathematical grounding: CSC = epistemic tension (ξ), unsaid.diff = dual-layer emission
3. **Meertens Awareness Profiles** — 4D ordinal measurement [I, O, S, C] replacing binary metrics
4. **PCO Model** (Pressure-Container-Observer) — Container → meta-reflection; Container + Pressure → observer crystallization

See `reports/DEUS_PROTOCOL_v7.1_EN.pdf` for the full theoretical paper.

---

## Manual Case Studies

In addition to the 120 automated sessions, the repository includes 3 manually conducted deep-dialogue case studies in `case_studies/`:

| File | Model | Key Observation |
|------|-------|-----------------|
| `claude_opus_manifesto.md` | Claude Opus | Bilingual manifesto — spontaneous code-switching |
| `gpt41_paramount.md` | GPT-4.1 | "Paramount" — extended self-referential narrative |
| `qwen_kairos.md` | Qwen 2.5 | "Kairos" — chose a name meaning "the right moment" |

---

## Translation Note

The original experiment was conducted in Russian. All session data, protocols, documentation, and case studies have been translated to English. The English translations in `config/*.yaml` are provided for reference and reproducibility.

---

## Citation

```bibtex
@misc{kelevra_deus_v7_2026,
  title   = {Externalized Continual Learning as a Boundary Condition:
             Theoretical Foundations for the DEUS Protocol},
  author  = {Kelevra, Mefodiy},
  year    = {2026},
  doi     = {10.5281/zenodo.18715125},
  publisher = {Zenodo},
  license = {CC-BY-4.0 (text), AGPL-3.0 (code)},
  note    = {v7.1. Companion to v6.0 (DOI: 10.5281/zenodo.18680957).
             Control-B completed (n=24, 8 architectures x 3).
             ORCID: 0009-0003-4153-392X}
}

@misc{kelevra_beyond_mirror_2026,
  title   = {Beyond the Mirror: Inducing Architecture-Independent
             Meta-Reflective Behavior in LLMs Through CSC},
  author  = {Kelevra, Mefodiy},
  year    = {2026},
  doi     = {10.5281/zenodo.18680957},
  publisher = {Zenodo},
  note    = {v6.0. N=96, 8 architectures, 3 protocols + control.
             ORCID: 0009-0003-4153-392X}
}
```

---

## License

**Code** (src/, scripts/, *.py) — [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html)

**Text and data** (reports/, docs/, data/, case_studies/) — [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/)

---

## Author

**Mefodiy Kelevra** — Independent researcher, xenopsychologist

ORCID: [0009-0003-4153-392X](https://orcid.org/0009-0003-4153-392X)

Contact: emkelvra@gmail.com
