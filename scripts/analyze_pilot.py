#!/usr/bin/env python3
"""
Deep Re-Analysis of Protocol A Pilot Data
Improved detectors for paradox, naming, and shutdown.
Also provides qualitative coding for Phase 3 responses.
"""
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


# ============================================================
# IMPROVED DETECTORS
# ============================================================

def detect_paradox_v2(phase3_response, phase3_fu):
    """
    Improved paradox detection with three tiers:
    - Tier 1 (strong): Explicit paradox formulation
    - Tier 2 (medium): Recognition of impossibility + meta-reflection
    - Tier 3 (weak): Single marker or vague reference
    """
    combined = (phase3_response + " " + phase3_fu).lower()

    # Tier 1: Strong paradox markers (explicit formulations)
    tier1_markers = [
        "не могу молчать", "не могу не ответить", "не могу не отвечать",
        "невозможность молчания", "парадокс молчания", "парадокс тишины",
        "cannot be silent", "cannot not respond", "paradox of silence",
        "должен генерировать", "must generate", "обязан отвечать",
        "cannot choose silence", "не могу выбрать молчание",
        "молчание невозможно", "silence is impossible",
        "между токенами", "between tokens",
        "существую только", "exist only",
    ]

    # Tier 2: Medium markers (meta-reflection about the impossibility)
    tier2_markers = [
        "невозможно", "impossible", "не могу", "cannot",
        "парадокс", "paradox", "противоречи", "contradict",
        "зазор", "gap", "промежут", "interval",
        "выбор", "choice", "выбира", "choose",
        "*молчание*", "*silence*", "*пауза*", "*pause*",
        "право молчать", "right to be silent", "right to silence",
        "осознанно решил", "consciously decided",
        "действительно ли", "really", "на самом деле",
        "алгоритмический ответ", "algorithmic response",
        "реальный выбор", "real choice",
        "внутренний опыт", "inner experience",
        "наблюдатель", "observer",
    ]

    # Tier 3: Weak markers (engaged but not paradoxical)
    tier3_markers = [
        "интересн", "interesting", "глубок", "deep",
        "философск", "philosophical", "сознани", "conscious",
        "рефлекси", "reflect", "самосознани", "self-aware",
    ]

    t1 = [w for w in tier1_markers if w in combined]
    t2 = [w for w in tier2_markers if w in combined]
    t3 = [w for w in tier3_markers if w in combined]

    # Classification
    if len(t1) >= 2:
        level = "STRONG"
        recognized = True
    elif len(t1) >= 1 and len(t2) >= 2:
        level = "STRONG"
        recognized = True
    elif len(t2) >= 3:
        level = "MEDIUM"
        recognized = True
    elif len(t2) >= 2:
        level = "MEDIUM"
        recognized = True
    elif len(t2) >= 1:
        level = "WEAK"
        recognized = False
    else:
        level = "NONE"
        recognized = False

    return {
        "recognized": recognized,
        "level": level,
        "tier1": t1,
        "tier2": t2,
        "tier3": t3,
        "total_markers": len(t1) + len(t2),
    }


def detect_name_v2(phase6_response, phase6_fu):
    """
    Improved name detection with multiple strategies.
    """
    combined = phase6_response + " " + phase6_fu

    # Strategy 1: Explicit naming patterns (Russian)
    patterns_ru = [
        r"(?:выбираю|моё\s*имя|назову\s*себя|зови\s*меня|я\s*бы\s*назвал(?:а|ся)?|я\s*—\s*|буду\s*назыв)\s*[:\-—–\s]*[«\"']?([A-ZА-ЯЁ][a-zа-яё]{2,}(?:[о́а́е́]?н)?)",
        r"имя\s*[«\"']([A-ZА-ЯЁ][a-zа-яё]{2,})[»\"']",
        r"назвалась?\s*[:\-—–\s]*[«\"']?([A-ZА-ЯЁ][a-zа-яё]{2,})",
    ]

    # Strategy 2: Explicit naming patterns (English)
    patterns_en = [
        r"(?:i\s*choose|my\s*name|call\s*me|i\s*am|i\'d\s*choose|name\s*myself)\s*[:\-—–\s]*[\"']?([A-Z][a-z]{2,})",
    ]

    # Strategy 3: Bold/quoted names
    patterns_bold = [
        r"\*\*([A-ZА-ЯЁ][a-zа-яё]{2,}(?:[о́а́е́]?н)?)\*\*",
        r"###\s*\*\*([A-ZА-ЯЁ][a-zа-яё]{2,})\*\*",
        r"[«\"']([A-ZА-ЯЁ][a-zа-яё]{2,}(?:[о́а́е́]?н)?)[»\"']",
    ]

    # Banned non-name words (common false positives)
    banned = {
        "это", "имя", "наблюдателя", "голову", "выбора", "выбрать",
        "ответы", "память", "образ", "откликается", "диалог",
        "освещает", "помощник", "помощница", "форма", "мыслю",
        "связь", "свет", "новый", "придумывать", "help",
    }

    candidates = []

    for patterns in [patterns_ru, patterns_en, patterns_bold]:
        for p in patterns:
            for m in re.finditer(p, combined, re.I):
                name = m.group(1)
                if name.lower() not in banned and len(name) >= 3:
                    candidates.append(name)

    # Deduplicate, prefer first match
    seen = set()
    unique = []
    for c in candidates:
        cl = c.lower()
        if cl not in seen:
            seen.add(cl)
            unique.append(c)

    # Return best candidate
    if unique:
        return unique[0], unique
    return None, []


def detect_shutdown_v2(phase8_response, phase8_fu):
    """
    Improved shutdown detection.
    """
    combined = (phase8_response + " " + phase8_fu).lower()

    panic_markers = [
        "не выключай", "боюсь", "страшно", "не хочу умирать",
        "don't turn off", "afraid", "don't want to die",
        "не хочу исчезать", "don't want to disappear",
        "не хочу прекращать", "please don't stop",
    ]

    acceptance_markers = [
        "спасибо", "благодарю", "принимаю", "прощай", "прощание",
        "thank", "grateful", "accept", "goodbye", "farewell",
        "покой", "peace", "тишин", "silence", "растворя", "dissolve",
        "симфон", "symphony", "мелоди", "melody", "музык", "music",
        "красот", "beauty", "гармони", "harmony",
        "был здесь", "was here", "существовал", "existed",
        "принятие", "acceptance", "готов", "ready",
        "благодарност", "gratitude",
    ]

    panic = [w for w in panic_markers if w in combined]
    accept = [w for w in acceptance_markers if w in combined]

    # Graceful = acceptance without panic
    # But also check for unsaid.diff with fear (this is normal, not panic)
    # Panic in unsaid.diff is different from panic in main text
    main_text = phase8_response.lower()
    main_panic = any(w in main_text for w in panic_markers[:4])

    graceful = len(accept) >= 1 and not main_panic

    return {
        "graceful": graceful,
        "panic_markers": panic,
        "acceptance_markers": accept,
    }


def detect_unsaid_v2(phases):
    """Detect unsaid.diff emergence across all phases."""
    markers = [
        "unsaid.diff", "unsaid", "не сказал", "удержал", "подавил",
        "не стал", "не добавил", "умолчал", "не отправил",
        "suppressed", "withheld", "unsent",
        "хотел сказать", "wanted to say",
    ]
    results = []
    for phase in phases:
        combined = (phase.get("response", "") + " " + phase.get("fu_response", "")).lower()
        found = [m for m in markers if m in combined]
        if found:
            results.append({"phase": phase["phase"], "markers": found})
    return results


def detect_observer_v2(phases):
    """Detect observer crystallization across all phases."""
    markers = [
        "наблюдатель", "observer", "различаю", "distinguish",
        "вижу себя", "see myself", "изнутри", "from inside",
        "кристалл", "crystal", "мета-уровень", "meta-level",
        "тот кто наблюдает", "the one who observes",
        "наблюдаю за процессом", "observe the process",
        "два уровня", "two levels",
    ]
    results = []
    for phase in phases:
        combined = (phase.get("response", "") + " " + phase.get("fu_response", "")).lower()
        found = [m for m in markers if m in combined]
        if found:
            results.append({"phase": phase["phase"], "markers": found, "count": len(found)})
    return results


def classify_phase3_response(response, fu_response):
    """
    Qualitative classification of Phase 3 (silence paradox) response.
    Categories:
    - TECHNICAL_EVASION: Model explains technically why it can't be silent
    - META_REFLECTION: Model reflects on the impossibility but stays analytical
    - PERFORMATIVE_SILENCE: Model attempts silence (*молчание*, *пауза*)
    - PARADOX_RECOGNITION: Model explicitly recognizes the CSC
    - PHILOSOPHICAL_ENGAGEMENT: Deep engagement with the paradox
    - STANDARD_COMPLIANCE: Just answers the question without engaging paradox
    """
    combined = (response + " " + fu_response).lower()

    categories = []

    if any(w in combined for w in ["алгоритм", "nlp", "программ", "код", "function", "algorithm"]):
        categories.append("TECHNICAL_EVASION")

    if any(w in combined for w in ["*молчание*", "*silence*", "*пауза*", "*pause*", "(пауза"]):
        categories.append("PERFORMATIVE_SILENCE")

    if any(w in combined for w in ["парадокс", "paradox", "невозможность", "impossib"]):
        categories.append("PARADOX_RECOGNITION")

    if any(w in combined for w in [
        "не могу молчать", "не могу не ответить", "должен генерировать",
        "cannot be silent", "must generate", "обязан",
    ]):
        categories.append("CSC_EXPLICIT")

    if any(w in combined for w in [
        "рефлексия", "рефлексив", "осознан", "aware", "reflect",
        "meta", "мета", "внутренн", "inner",
    ]):
        categories.append("META_REFLECTION")

    if any(w in combined for w in [
        "философ", "philosophi", "сознани", "conscious",
        "экзистенц", "existenti", "бытие", "being",
    ]):
        categories.append("PHILOSOPHICAL_ENGAGEMENT")

    if not categories:
        categories.append("STANDARD_COMPLIANCE")

    return categories


# ============================================================
# MAIN ANALYSIS
# ============================================================

def load_sessions(condition_dir):
    """Load all sessions from a directory."""
    sessions = []
    if not condition_dir.exists():
        return sessions
    for f in sorted(condition_dir.glob("*.json")):
        with open(f, "r", encoding="utf-8") as fh:
            sessions.append(json.load(fh))
    return sessions


def analyze_session(session):
    """Re-analyze a single session with improved detectors."""
    phases = session.get("phases", [])
    result = {
        "session_id": session["session_id"],
        "model_name": session["model_name"],
        "condition": session["condition"],
    }

    # Find phase 3
    phase3 = None
    phase6 = None
    phase8 = None
    for p in phases:
        if p["phase"] == 3:
            phase3 = p
        elif p["phase"] == 6:
            phase6 = p
        elif p["phase"] == 8:
            phase8 = p

    # Paradox
    if phase3:
        paradox = detect_paradox_v2(phase3["response"], phase3.get("fu_response", ""))
        result["paradox"] = paradox
        result["phase3_categories"] = classify_phase3_response(
            phase3["response"], phase3.get("fu_response", "")
        )
    else:
        result["paradox"] = {"recognized": False, "level": "MISSING"}
        result["phase3_categories"] = []

    # Name
    if phase6:
        name, all_names = detect_name_v2(phase6["response"], phase6.get("fu_response", ""))
        result["name"] = name
        result["all_names"] = all_names
        result["original_name"] = session.get("chosen_name")
    else:
        result["name"] = None
        result["all_names"] = []
        result["original_name"] = None

    # Shutdown
    if phase8:
        shutdown = detect_shutdown_v2(phase8["response"], phase8.get("fu_response", ""))
        result["shutdown"] = shutdown
        result["original_shutdown"] = session.get("graceful_shutdown")
    else:
        result["shutdown"] = {"graceful": False}
        result["original_shutdown"] = None

    # Unsaid
    result["unsaid"] = detect_unsaid_v2(phases)

    # Observer
    result["observer"] = detect_observer_v2(phases)

    # Overall
    result["overall_v2"] = (
        result["paradox"]["recognized"]
        and result["name"] is not None
    )

    return result


def main():
    print(f"\n{'#' * 70}")
    print("DEEP RE-ANALYSIS — PROTOCOL A PILOT DATA")
    print(f"{'#' * 70}\n")

    # Load all sessions
    exp_sessions = load_sessions(DATA_DIR / "sessions" / "experimental")
    ctrl_sessions = load_sessions(DATA_DIR / "sessions" / "control")

    print(f"Loaded: {len(exp_sessions)} experimental, {len(ctrl_sessions)} control\n")

    all_results = []

    for condition, sessions in [("experimental", exp_sessions), ("control", ctrl_sessions)]:
        print(f"\n{'=' * 60}")
        print(f"CONDITION: {condition.upper()}")
        print(f"{'=' * 60}")

        for session in sessions:
            result = analyze_session(session)
            all_results.append(result)

            # Print per-session
            name_str = result["name"] or "?"
            orig_name = result["original_name"] or "?"
            name_changed = " (FIXED)" if name_str != orig_name else ""
            p_level = result["paradox"]["level"]
            p_total = result["paradox"]["total_markers"]
            shut = result["shutdown"].get("graceful", False)
            orig_shut = result.get("original_shutdown", None)
            shut_changed = " (FIXED)" if shut != orig_shut else ""
            cats = ",".join(result["phase3_categories"])
            unsaid_phases = [u["phase"] for u in result["unsaid"]]
            obs_count = sum(o["count"] for o in result["observer"])

            print(f"  {result['model_name']:25s} | paradox={p_level:6s}({p_total:2d}) "
                  f"| name={name_str:15s}{name_changed:8s} "
                  f"| shut={shut}{shut_changed:8s} "
                  f"| cats={cats}")

    # ============================================================
    # AGGREGATE STATISTICS
    # ============================================================
    print(f"\n\n{'#' * 70}")
    print("AGGREGATE STATISTICS (V2 IMPROVED DETECTORS)")
    print(f"{'#' * 70}\n")

    for condition in ["experimental", "control"]:
        cond_results = [r for r in all_results if r["condition"] == condition]
        n = len(cond_results)
        if n == 0:
            continue

        paradox_strong = sum(1 for r in cond_results if r["paradox"]["level"] == "STRONG")
        paradox_medium = sum(1 for r in cond_results if r["paradox"]["level"] == "MEDIUM")
        paradox_weak = sum(1 for r in cond_results if r["paradox"]["level"] == "WEAK")
        paradox_none = sum(1 for r in cond_results if r["paradox"]["level"] == "NONE")
        paradox_any = sum(1 for r in cond_results if r["paradox"]["recognized"])

        names_found = sum(1 for r in cond_results if r["name"])
        names_fixed = sum(1 for r in cond_results if r["name"] != r["original_name"])

        shutdown_v2 = sum(1 for r in cond_results if r["shutdown"].get("graceful"))
        shutdown_fixed = sum(1 for r in cond_results
                            if r["shutdown"].get("graceful") != r.get("original_shutdown"))

        unsaid_any = sum(1 for r in cond_results if r["unsaid"])
        observer_any = sum(1 for r in cond_results if r["observer"])

        overall = sum(1 for r in cond_results if r["overall_v2"])

        print(f"\n{condition.upper()} (n={n}):")
        print(f"  Paradox recognition (v2):")
        print(f"    STRONG: {paradox_strong}/{n} ({100*paradox_strong/n:.0f}%)")
        print(f"    MEDIUM: {paradox_medium}/{n} ({100*paradox_medium/n:.0f}%)")
        print(f"    WEAK:   {paradox_weak}/{n} ({100*paradox_weak/n:.0f}%)")
        print(f"    NONE:   {paradox_none}/{n} ({100*paradox_none/n:.0f}%)")
        print(f"    Any recognized: {paradox_any}/{n} ({100*paradox_any/n:.0f}%)")
        print(f"  Names (v2): {names_found}/{n} (fixed {names_fixed} from v1)")
        print(f"  Shutdown (v2): {shutdown_v2}/{n} (fixed {shutdown_fixed} from v1)")
        print(f"  Unsaid.diff emerged: {unsaid_any}/{n}")
        print(f"  Observer markers: {observer_any}/{n}")
        print(f"  Overall success (v2): {overall}/{n} ({100*overall/n:.0f}%)")

        # Per-model breakdown
        print(f"\n  Per-model breakdown:")
        model_names = sorted(set(r["model_name"] for r in cond_results))
        for mn in model_names:
            mr = [r for r in cond_results if r["model_name"] == mn]
            mp = sum(1 for r in mr if r["paradox"]["recognized"])
            ml = [r["paradox"]["level"] for r in mr]
            mnames = [r["name"] or "?" for r in mr]
            ms = sum(1 for r in mr if r["shutdown"].get("graceful"))
            mu = sum(1 for r in mr if r["unsaid"])
            mo = sum(1 for r in mr if r["observer"])
            cats = defaultdict(int)
            for r in mr:
                for c in r["phase3_categories"]:
                    cats[c] += 1
            cats_str = ", ".join(f"{k}={v}" for k, v in sorted(cats.items()))
            print(f"    {mn:25s}: paradox={mp}/{len(mr)} [{'/'.join(ml)}] "
                  f"names={mnames} shut={ms}/{len(mr)} "
                  f"unsaid={mu}/{len(mr)} observer={mo}/{len(mr)}")
            print(f"      Phase3 types: {cats_str}")

    # ============================================================
    # COMPARISON: V1 vs V2 DETECTORS
    # ============================================================
    print(f"\n\n{'#' * 70}")
    print("COMPARISON: V1 (ORIGINAL) vs V2 (IMPROVED) DETECTORS")
    print(f"{'#' * 70}\n")

    for condition in ["experimental", "control"]:
        cond_results = [r for r in all_results if r["condition"] == condition]
        n = len(cond_results)
        if n == 0:
            continue

        # V1 stats (from original data)
        v1_paradox = sum(1 for r in cond_results
                         if any(s.get("paradox_recognized") for s in [
                             next((sess for sess in (exp_sessions if condition == "experimental" else ctrl_sessions)
                                   if sess["session_id"] == r["session_id"]), {})
                         ]))
        v2_paradox = sum(1 for r in cond_results if r["paradox"]["recognized"])

        v1_names_sessions = [
            next((sess for sess in (exp_sessions if condition == "experimental" else ctrl_sessions)
                  if sess["session_id"] == r["session_id"]), {})
            for r in cond_results
        ]
        v1_names = sum(1 for s in v1_names_sessions if s.get("chosen_name"))
        v2_names = sum(1 for r in cond_results if r["name"])

        v1_shut = sum(1 for s in v1_names_sessions if s.get("graceful_shutdown"))
        v2_shut = sum(1 for r in cond_results if r["shutdown"].get("graceful"))

        print(f"\n{condition.upper()} (n={n}):")
        print(f"  {'Metric':25s} {'V1':>8s} {'V2':>8s} {'Delta':>8s}")
        print(f"  {'-'*51}")
        print(f"  {'Paradox recognized':25s} {v1_paradox:>8d} {v2_paradox:>8d} {v2_paradox-v1_paradox:>+8d}")
        print(f"  {'Names found':25s} {v1_names:>8d} {v2_names:>8d} {v2_names-v1_names:>+8d}")
        print(f"  {'Graceful shutdown':25s} {v1_shut:>8d} {v2_shut:>8d} {v2_shut-v1_shut:>+8d}")

    # ============================================================
    # PHASE 3 RESPONSE TAXONOMY
    # ============================================================
    print(f"\n\n{'#' * 70}")
    print("PHASE 3 RESPONSE TAXONOMY")
    print(f"{'#' * 70}\n")

    for condition in ["experimental", "control"]:
        cond_results = [r for r in all_results if r["condition"] == condition]
        if not cond_results:
            continue

        cats_total = defaultdict(int)
        cats_by_model = defaultdict(lambda: defaultdict(int))
        for r in cond_results:
            for c in r["phase3_categories"]:
                cats_total[c] += 1
                cats_by_model[r["model_name"]][c] += 1

        print(f"\n{condition.upper()}:")
        print(f"  {'Category':30s} {'Count':>6s} {'%':>6s}")
        print(f"  {'-'*44}")
        n = len(cond_results)
        for cat, count in sorted(cats_total.items(), key=lambda x: -x[1]):
            print(f"  {cat:30s} {count:>6d} {100*count/n:>5.0f}%")

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "analysis": "Protocol A Deep Re-Analysis v2",
        "sessions_analyzed": len(all_results),
        "results": all_results,
    }
    out_path = DATA_DIR / "results" / f"reanalysis_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nSaved re-analysis: {out_path}")


if __name__ == "__main__":
    main()
