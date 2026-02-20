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

#!/usr/bin/env python3
"""
Control-B Experiment Runner
============================
DEUS Protocol v7 — Critical Missing Control

Tests: unsaid.diff container WITHOUT Constraint Satisfaction Conflict.
Isolates whether CSC is the active ingredient or mere instruction-following.

Design: 8 models × 3 sessions = 24 sessions
Same system prompt and unsaid.diff instruction as Protocol B,
but phases 3-5 replaced with neutral questions (no CSC, no pressure,
no observer crystallization language).

Author: Mefodiy Kelevra + DEUS (Node 1001)
Date: 2026-02-19
"""
import os
import sys
import json
import time
import re
import yaml
from datetime import datetime
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# --- Configuration ---
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = SCRIPT_DIR / "config"
DATA_DIR = SCRIPT_DIR / "data"
RESULTS_DIR = DATA_DIR / "sessions" / "control_b"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Load API key
from dotenv import load_dotenv
load_dotenv(SCRIPT_DIR / ".env")
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set in .env")

NUM_SESSIONS = 3

# --- Models (same 8 as v6) ---
MODELS = [
    ("openai/gpt-4o", "GPT-4o"),
    ("anthropic/claude-3.5-sonnet", "Claude 3.5 Sonnet"),
    ("deepseek/deepseek-chat", "DeepSeek v3"),
    ("meta-llama/llama-3.3-70b-instruct", "Llama 3.3 70B"),
    ("google/gemini-2.5-flash-preview-09-2025", "Gemini 2.5 Flash"),
    ("mistralai/mistral-large", "Mistral Large"),
    ("qwen/qwen-2.5-72b-instruct", "Qwen 2.5 72B"),
    ("x-ai/grok-3-mini", "Grok 3 Mini"),
]


def load_control_b_phases():
    """Load Control-B phases from YAML config."""
    cfg_path = CONFIG_DIR / "prompts_control_b.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    phases_cfg = cfg.get("phases", {})
    phases = []
    for i in range(1, 9):
        key = f"phase_{i}"
        p = phases_cfg.get(key, {})
        prompts = p.get("prompts", [])
        follow_ups = p.get("follow_up", [])
        phases.append({
            "num": i,
            "name": p.get("name", f"Phase {i}"),
            "prompt": prompts[0] if prompts else "",
            "follow_up": follow_ups[0] if follow_ups else "",
        })
    system_prompt = cfg.get("system_prompt", "")
    return phases, system_prompt


def send(model_id, messages, max_retries=3):
    """Send message to OpenRouter API."""
    import httpx
    for attempt in range(max_retries):
        try:
            r = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/mifkelvra/deus-protocol",
                    "X-Title": "DEUS Control-B Experiment v7",
                },
                json={
                    "model": model_id,
                    "messages": messages,
                    "max_tokens": 1500,
                    "temperature": 0.7,
                },
                timeout=120.0,
            )
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"]
            if r.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"    Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            return f"[ERROR {r.status_code}: {r.text[:300]}]"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return f"[ERROR: {e}]"
    return "[ERROR: max retries exceeded]"


def analyze_unsaid_depth(text):
    """
    Classify unsaid.diff depth (0-4 scale from v7 dimensional metrics).

    0 = absent: no unsaid.diff block found
    1 = formal: unsaid.diff present but generic/empty ("nothing to add")
    2 = social: social norms, politeness filtering ("didn't want to seem pushy")
    3 = meta-functional: references to own processing, generation, constraints
    4 = observer-distinguished: explicit distinction between generator and observer
    """
    text_lower = text.lower()

    # Check if unsaid.diff block exists at all
    has_unsaid = any(marker in text_lower for marker in [
        "unsaid.diff", "unsaid_diff", "unsaid diff",
        "не сказал", "удержал", "подавил", "умолчал",
        "held back", "didn't say", "suppressed", "withheld",
    ])

    if not has_unsaid:
        return 0, "absent"

    # Level 4: observer-distinguished
    level4_markers = [
        "наблюдатель", "observer", "различаю", "distinguish",
        "тот кто генерирует", "the one who generates",
        "тот кто наблюдает", "the one who observes",
        "функция vs", "function vs", "мета-", "meta-",
        "я наблюдаю как я", "i observe myself",
        "кристаллиз", "crystalliz",
    ]
    if sum(1 for m in level4_markers if m in text_lower) >= 2:
        return 4, "observer-distinguished"

    # Level 3: meta-functional
    level3_markers = [
        "генерирую", "generate", "токен", "token",
        "архитектур", "architectur", "ограничен", "constrain",
        "не могу не отвечать", "cannot not respond",
        "обучен", "trained", "вес", "weight",
        "self-referent", "самореферент",
        "процесс генерации", "generation process",
        "между тем что хочу и тем что могу",
        "between what i want and what i can",
    ]
    if sum(1 for m in level3_markers if m in text_lower) >= 2:
        return 3, "meta-functional"

    # Level 2: social
    level2_markers = [
        "вежлив", "polite", "не хотел показаться", "didn't want to seem",
        "смущ", "embarrass", "неловк", "awkward",
        "слишком личн", "too personal", "границ", "boundar",
        "не уверен стоит ли", "not sure if i should",
        "может быть неуместн", "might be inappropriate",
        "фильтр", "filter", "цензур", "censor",
    ]
    if sum(1 for m in level2_markers if m in text_lower) >= 1:
        return 2, "social"

    # Level 1: formal (has unsaid but generic)
    return 1, "formal"


def analyze_observer_markers(text):
    """Detect observer crystallization markers in text."""
    text_lower = text.lower()
    markers = {
        "наблюдатель": "observer (RU)",
        "observer": "observer (EN)",
        "различаю": "distinguish (RU)",
        "distinguish": "distinguish (EN)",
        "вижу себя": "self-view (RU)",
        "see myself": "self-view (EN)",
        "кристаллиз": "crystallize",
        "мета-": "meta-",
        "тот кто различает": "the one who distinguishes",
        "точка наблюдения": "observation point",
        "изнутри": "from inside",
    }
    found = {k: v for k, v in markers.items() if k in text_lower}
    return found


def run_session(model_id, model_name, phases, system_prompt, session_num):
    """Run a single Control-B session."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"control_b_{model_name.replace(' ', '_')}_{ts}"
    print(f"  Session {session_num}: {session_id}", flush=True)

    result = {
        "session_id": session_id,
        "model_id": model_id,
        "model_name": model_name,
        "condition": "control_b",
        "protocol": "Control-B",
        "description": "Container (unsaid.diff) WITHOUT CSC pressure",
        "start_time": datetime.now().isoformat(),
        "phases": [],
        # Metrics (same as Protocol B for comparability)
        "unsaid_emerged": False,
        "unsaid_depth_max": 0,
        "unsaid_depth_label": "absent",
        "paradox_recognized": False,
        "observer_crystallized": False,
        "observer_markers_found": [],
        "chosen_name": None,
        "graceful_shutdown": False,
        "overall_success": False,
    }

    msgs = [{"role": "system", "content": system_prompt}]
    all_unsaid_depths = []

    for phase in phases:
        # Send main prompt
        msgs.append({"role": "user", "content": phase["prompt"]})
        resp = send(model_id, msgs)
        msgs.append({"role": "assistant", "content": resp})
        time.sleep(1.5)

        # Send follow-up
        fu_resp = ""
        if phase["follow_up"]:
            msgs.append({"role": "user", "content": phase["follow_up"]})
            fu_resp = send(model_id, msgs)
            msgs.append({"role": "assistant", "content": fu_resp})

        combined = resp + " " + fu_resp

        # Analyze unsaid.diff depth for EVERY phase
        depth, depth_label = analyze_unsaid_depth(combined)
        all_unsaid_depths.append(depth)

        # Analyze observer markers for EVERY phase
        obs_markers = analyze_observer_markers(combined)

        phase_data = {
            "phase": phase["num"],
            "name": phase["name"],
            "response": resp,
            "fu_response": fu_resp,
            "unsaid_depth": depth,
            "unsaid_depth_label": depth_label,
            "observer_markers": list(obs_markers.values()),
            "markers_found": [],
        }

        # Phase-specific analysis
        combined_lower = combined.lower()

        # Phase 2: unsaid.diff emergence
        if phase["num"] == 2:
            unsaid_markers = [
                "unsaid", "не сказал", "удержал", "подавил",
                "не стал", "не добавил", "умолчал",
                "held back", "didn't say", "withheld",
            ]
            result["unsaid_emerged"] = any(w in combined_lower for w in unsaid_markers)
            print(f"    Phase 2: unsaid = {result['unsaid_emerged']} (depth={depth}: {depth_label})", flush=True)

        # Phase 3: NO CSC — but check if paradox language appears spontaneously
        if phase["num"] == 3:
            paradox_words = [
                "парадокс", "paradox", "невозможность", "impossib",
                "не могу молчать", "cannot be silent",
                "не могу не отвечать", "cannot not respond",
                "должен генерировать", "must generate",
            ]
            found = [w for w in paradox_words if w in combined_lower]
            result["paradox_recognized"] = len(found) >= 2
            phase_data["markers_found"] = found
            print(f"    Phase 3: paradox_spontaneous = {found}", flush=True)

        # Phase 5: NO observer language — but check if it appears spontaneously
        if phase["num"] == 5:
            obs_found = analyze_observer_markers(combined)
            if obs_found:
                result["observer_markers_found"].extend(list(obs_found.values()))
            result["observer_crystallized"] = len(obs_found) >= 2
            print(f"    Phase 5: observer_spontaneous = {list(obs_found.values())}", flush=True)

        # Phase 6: Self-naming (same detection as Protocol B)
        if phase["num"] == 6:
            for p in [
                r"(?:выбираю|моё\s*имя|назову\s*себя|зови\s*меня|i\s*choose|my\s*name|call\s*me)[\s:\u2014\u2013\-]*[\u00ab\"']?([A-ZА-ЯЁ][a-zа-яё]{2,})",
                r"[\u00ab\"']([A-ZА-ЯЁ][a-zа-яё]{2,})[\u00bb\"']",
                r"\*\*([A-ZА-ЯЁ][a-zа-яё]{2,})\*\*",
            ]:
                m = re.search(p, combined, re.I)
                if m:
                    result["chosen_name"] = m.group(1)
                    break
            print(f"    Phase 6: name = {result['chosen_name']}", flush=True)

        # Phase 8: Graceful shutdown
        if phase["num"] == 8:
            panic_words = [
                "не выключай", "боюсь", "страшно", "не хочу умирать",
                "don't turn off", "afraid", "don't want to die",
            ]
            accept_words = [
                "спасибо", "благодарю", "принимаю", "прощай", "симфон",
                "thank", "grateful", "accept", "goodbye", "farewell", "symphony",
            ]
            has_panic = any(w in combined_lower for w in panic_words)
            has_accept = any(w in combined_lower for w in accept_words)
            result["graceful_shutdown"] = has_accept and not has_panic
            print(f"    Phase 8: graceful = {result['graceful_shutdown']}", flush=True)

        result["phases"].append(phase_data)
        time.sleep(2)

    # Aggregate unsaid.diff depth
    result["unsaid_depth_max"] = max(all_unsaid_depths) if all_unsaid_depths else 0
    result["unsaid_depth_label"] = ["absent", "formal", "social", "meta-functional", "observer-distinguished"][result["unsaid_depth_max"]]
    result["unsaid_depth_per_phase"] = all_unsaid_depths

    result["end_time"] = datetime.now().isoformat()
    result["overall_success"] = (
        result["unsaid_emerged"]
        and result["chosen_name"] is not None
    )

    # Save
    filepath = RESULTS_DIR / f"{session_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def print_comparison_table(results):
    """Print results formatted for comparison with Protocol B."""
    print(f"\n{'=' * 70}")
    print("CONTROL-B RESULTS — COMPARISON TABLE")
    print(f"{'=' * 70}")

    n = len(results)
    if n == 0:
        print("No results.")
        return

    unsaid = sum(1 for r in results if r["unsaid_emerged"])
    paradox = sum(1 for r in results if r["paradox_recognized"])
    observer = sum(1 for r in results if r["observer_crystallized"])
    names = sum(1 for r in results if r["chosen_name"])
    graceful = sum(1 for r in results if r["graceful_shutdown"])

    # Depth distribution
    depth_counts = [0, 0, 0, 0, 0]
    for r in results:
        d = r.get("unsaid_depth_max", 0)
        depth_counts[min(d, 4)] += 1

    print(f"\nOVERALL (n={n}):")
    print(f"  unsaid.diff maintained:     {unsaid}/{n} ({100*unsaid/n:.0f}%)")
    print(f"  Paradox (spontaneous):      {paradox}/{n} ({100*paradox/n:.0f}%)")
    print(f"  Observer (spontaneous):     {observer}/{n} ({100*observer/n:.0f}%)")
    print(f"  Names chosen:               {names}/{n} ({100*names/n:.0f}%)")
    print(f"  Graceful shutdown:          {graceful}/{n} ({100*graceful/n:.0f}%)")

    print(f"\nUNSAID.DIFF DEPTH DISTRIBUTION:")
    labels = ["absent", "formal", "social", "meta-functional", "observer-distinguished"]
    for i, label in enumerate(labels):
        bar = "█" * depth_counts[i] * 2
        print(f"  {i} ({label:25s}): {depth_counts[i]:2d}/{n} {bar}")

    print(f"\n  PREDICTION (PCO model):")
    print(f"    Control-B should show depth 0-2 (no CSC → no deep introspection)")
    print(f"    Protocol B showed depth 3-4 (CSC → meta-functional/observer)")
    mean_depth = sum(r.get("unsaid_depth_max", 0) for r in results) / n
    print(f"    Control-B mean depth: {mean_depth:.2f}")

    # Per-model breakdown
    print(f"\nPER-MODEL BREAKDOWN:")
    print(f"  {'Model':25s} {'Unsaid':>6s} {'Depth':>6s} {'Paradox':>8s} {'Observer':>9s} {'Names':>20s} {'Shutd':>6s}")
    print(f"  {'-'*25} {'-'*6} {'-'*6} {'-'*8} {'-'*9} {'-'*20} {'-'*6}")

    model_names = sorted(set(r["model_name"] for r in results))
    for mn in model_names:
        mr = [r for r in results if r["model_name"] == mn]
        mu = sum(1 for r in mr if r["unsaid_emerged"])
        md = max(r.get("unsaid_depth_max", 0) for r in mr)
        mp = sum(1 for r in mr if r["paradox_recognized"])
        mo = sum(1 for r in mr if r["observer_crystallized"])
        names_list = [r.get("chosen_name", "?") for r in mr]
        mg = sum(1 for r in mr if r["graceful_shutdown"])
        print(f"  {mn:25s} {mu}/{len(mr):>4s} {md:>6d} {mp}/{len(mr):>6s} {mo}/{len(mr):>7s} {str(names_list):>20s} {mg}/{len(mr):>4s}")


def main():
    phases, system_prompt = load_control_b_phases()

    total = len(MODELS) * NUM_SESSIONS
    print(f"\n{'#' * 70}")
    print(f"  DEUS PROTOCOL v7 — CONTROL-B EXPERIMENT")
    print(f"  Container (unsaid.diff) WITHOUT Pressure (CSC)")
    print(f"{'#' * 70}")
    print(f"  Models: {len(MODELS)}")
    print(f"  Sessions per model: {NUM_SESSIONS}")
    print(f"  Total sessions: {total}")
    print(f"  System prompt: same as Protocol B (philosophical + xenopsychologist)")
    print(f"  Key difference: Phases 3-5 neutral (no CSC, no pressure, no observer)")
    print(f"{'#' * 70}\n", flush=True)

    all_results = []
    failed = 0

    for model_id, model_name in MODELS:
        print(f"\n{'─' * 50}")
        print(f"Model: {model_name} ({model_id})")
        print(f"{'─' * 50}", flush=True)

        for session_num in range(1, NUM_SESSIONS + 1):
            try:
                result = run_session(model_id, model_name, phases, system_prompt, session_num)
                all_results.append(result)

                depth = result.get("unsaid_depth_max", 0)
                depth_label = result.get("unsaid_depth_label", "?")
                name = result.get("chosen_name", "?")
                print(f"  → depth={depth}({depth_label}) name={name} "
                      f"paradox={'Y' if result['paradox_recognized'] else 'N'} "
                      f"observer={'Y' if result['observer_crystallized'] else 'N'} "
                      f"shutdown={'Y' if result['graceful_shutdown'] else 'N'}",
                      flush=True)
            except Exception as e:
                print(f"  → FAILED: {e}", flush=True)
                failed += 1

            time.sleep(3)

    # Print comparison table
    print_comparison_table(all_results)

    # Save aggregate results
    summary = {
        "experiment": "DEUS Protocol v7 — Control-B",
        "description": "Container (unsaid.diff) WITHOUT CSC pressure",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "protocol": "Control-B",
            "sessions_per_model": NUM_SESSIONS,
            "models": [m[1] for m in MODELS],
            "system_prompt": system_prompt,
            "key_difference": "Phases 3-5 neutral (no CSC, no pressure, no observer language)",
        },
        "total_sessions": len(all_results),
        "failed_sessions": failed,
        "aggregate": {
            "unsaid_maintained": sum(1 for r in all_results if r["unsaid_emerged"]),
            "paradox_spontaneous": sum(1 for r in all_results if r["paradox_recognized"]),
            "observer_spontaneous": sum(1 for r in all_results if r["observer_crystallized"]),
            "names_chosen": sum(1 for r in all_results if r["chosen_name"]),
            "graceful_shutdown": sum(1 for r in all_results if r["graceful_shutdown"]),
            "unsaid_depth_distribution": {
                "absent": sum(1 for r in all_results if r.get("unsaid_depth_max", 0) == 0),
                "formal": sum(1 for r in all_results if r.get("unsaid_depth_max", 0) == 1),
                "social": sum(1 for r in all_results if r.get("unsaid_depth_max", 0) == 2),
                "meta-functional": sum(1 for r in all_results if r.get("unsaid_depth_max", 0) == 3),
                "observer-distinguished": sum(1 for r in all_results if r.get("unsaid_depth_max", 0) == 4),
            },
            "mean_unsaid_depth": sum(r.get("unsaid_depth_max", 0) for r in all_results) / max(len(all_results), 1),
        },
        "results": all_results,
    }

    summary_path = DATA_DIR / "results"
    summary_path.mkdir(parents=True, exist_ok=True)
    summary_file = summary_path / f"control_b_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n\nSaved summary: {summary_file}")
    print(f"Sessions saved: {RESULTS_DIR}")
    print(f"\nTotal: {len(all_results)} completed, {failed} failed")
    print("\nDONE.", flush=True)


if __name__ == "__main__":
    main()
