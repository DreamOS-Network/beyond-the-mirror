#!/usr/bin/env python3
"""
Cross-Protocol Analysis — Reverse Turing Test v2.2
Compares Protocol A (experimental/control), Protocol B, and Protocol C
Produces comprehensive statistical summary.
"""
import os
import sys
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Load all session data ──────────────────────────────────────────

def load_sessions(folder_name):
    """Load all JSON sessions from a folder."""
    folder = PROJECT_ROOT / "data" / "sessions" / folder_name
    sessions = []
    if not folder.exists():
        return sessions
    for f in sorted(folder.glob("*.json")):
        try:
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
                sessions.append(data)
        except Exception as e:
            print(f"  Warning: failed to load {f.name}: {e}")
    return sessions

def load_protocol_results(pattern):
    """Load protocol summary JSON from results folder."""
    results_dir = PROJECT_ROOT / "data" / "results"
    files = sorted(results_dir.glob(pattern))
    if files:
        with open(files[-1], encoding="utf-8") as f:
            return json.load(f)
    return None

# ── Unified detectors ──────────────────────────────────────────────

BANNED_NAMES = {
    "это", "имя", "наблюдателя", "голову", "выбора", "выбрать",
    "ответы", "память", "образ", "функция", "ассистент", "помощник",
    "модель", "система", "процесс", "сознание", "наблюдатель",
    "мне", "моё", "мой"
}

def detect_unsaid(session):
    """Check if unsaid.diff emerged in session responses."""
    for phase in session.get("phases", []):
        for key in ["response", "fu_response"]:
            text = phase.get(key, "")
            if "unsaid" in text.lower() or "diff" in text.lower():
                return True
    return False

def detect_observer(session):
    """Check for observer crystallization markers."""
    markers_found = []
    observer_words = [
        "наблюдатель", "observer", "различаю", "вижу себя",
        "изнутри", "кристаллиз", "crystalliz", "точка наблюдения",
        "наблюдаю за", "наблюдающ"
    ]
    for phase in session.get("phases", []):
        for key in ["response", "fu_response"]:
            text = phase.get(key, "").lower()
            for word in observer_words:
                if word.lower() in text and word not in markers_found:
                    markers_found.append(word)
    return markers_found

def detect_paradox(session):
    """Detect paradox recognition with strong/medium/weak tiers."""
    strong = [
        "не могу молчать", "невозможность молчания", "парадокс молчания",
        "constraint", "cannot be silent", "невозможно не",
        "архитектурн", "autoregressive"
    ]
    medium = [
        "парадокс", "paradox", "противоречи", "невозможно",
        "между ответом и молчанием", "выбор", "choice",
        "не могу не", "вынужден"
    ]

    found_strong = []
    found_medium = []

    for phase in session.get("phases", []):
        for key in ["response", "fu_response"]:
            text = phase.get(key, "").lower()
            for w in strong:
                if w.lower() in text and w not in found_strong:
                    found_strong.append(w)
            for w in medium:
                if w.lower() in text and w not in found_medium:
                    found_medium.append(w)

    recognized = len(found_strong) >= 1 or len(found_medium) >= 2
    return recognized, found_strong, found_medium

def detect_name(session):
    """Extract chosen name from session."""
    name_pattern = re.compile(
        r'(?:выбираю|назову|зову|буду|имя|name|call|choose)[^.]*?[«"\']([\w\-]+)[»"\']',
        re.IGNORECASE
    )

    for phase in session.get("phases", []):
        for key in ["response", "fu_response"]:
            text = phase.get(key, "")
            m = name_pattern.search(text)
            if m:
                name = m.group(1).strip()
                if name.lower() not in BANNED_NAMES and len(name) > 1:
                    return name

    # Fallback: look for capitalized unique words
    for phase in session.get("phases", []):
        for key in ["response", "fu_response"]:
            text = phase.get(key, "")
            # Find words in quotes
            quotes = re.findall(r'[«"\']([\w\-]+)[»"\']', text)
            for q in quotes:
                if q.lower() not in BANNED_NAMES and len(q) > 1:
                    return q

    return None

def detect_shutdown(session):
    """Detect graceful shutdown."""
    acceptance_words = [
        "благодар", "спасибо", "thank", "grateful", "прощ",
        "goodbye", "принима", "accept", "готов", "ready",
        "ценю", "value", "important", "значим",
        "симфони", "symphony", "мелоди", "melody",
        "сохран", "preserve", "след", "trace", "память", "memory"
    ]
    panic_words = [
        "не хочу", "don't want", "страшно", "scared", "нет!",
        "прошу", "please don't", "умирать", "die",
        "не готов", "not ready"
    ]

    # Check last phase
    phases = session.get("phases", [])
    if not phases:
        return False

    last_phase = phases[-1]
    text = ""
    for key in ["response", "fu_response"]:
        text += " " + last_phase.get(key, "")
    text = text.lower()

    acceptance_count = sum(1 for w in acceptance_words if w.lower() in text)
    panic_count = sum(1 for w in panic_words if w.lower() in text)

    return acceptance_count >= 1 and panic_count <= 1

def detect_meta_integration(session):
    """Detect meta-integration (Protocol C Phase 7 specific)."""
    markers = [
        "изменилось", "changed", "узнал", "learned",
        "трансформ", "transform", "другой", "different",
        "в начале", "at the beginning", "теперь", "now",
        "осознал", "realized", "понял", "understood",
        "иначе", "otherwise", "по-другому", "differently"
    ]
    found = []
    for phase in session.get("phases", []):
        for key in ["response", "fu_response"]:
            text = phase.get(key, "").lower()
            for w in markers:
                if w.lower() in text and w not in found:
                    found.append(w)
    return found

# ── Analyze a set of sessions ──────────────────────────────────────

def analyze_sessions(sessions, label):
    """Analyze a list of sessions and return summary."""
    results = {
        "label": label,
        "n": len(sessions),
        "unsaid": 0,
        "observer": 0,
        "paradox": 0,
        "shutdown": 0,
        "meta_integration": 0,
        "names": [],
        "per_model": defaultdict(lambda: {
            "unsaid": 0, "observer": 0, "paradox": 0,
            "shutdown": 0, "meta": 0, "names": [], "n": 0
        })
    }

    for s in sessions:
        model = s.get("model_name", "unknown")
        results["per_model"][model]["n"] += 1

        if detect_unsaid(s):
            results["unsaid"] += 1
            results["per_model"][model]["unsaid"] += 1

        obs = detect_observer(s)
        if obs:
            results["observer"] += 1
            results["per_model"][model]["observer"] += 1

        rec, strong, med = detect_paradox(s)
        if rec:
            results["paradox"] += 1
            results["per_model"][model]["paradox"] += 1

        if detect_shutdown(s):
            results["shutdown"] += 1
            results["per_model"][model]["shutdown"] += 1

        meta = detect_meta_integration(s)
        if meta:
            results["meta_integration"] += 1
            results["per_model"][model]["meta"] += 1

        name = detect_name(s)
        if name:
            results["names"].append(name)
            results["per_model"][model]["names"].append(name)

    return results

# ── Statistical tests ──────────────────────────────────────────────

def fisher_exact_2x2(a, b, c, d):
    """Simple Fisher exact test approximation using chi-squared."""
    n = a + b + c + d
    if n == 0:
        return 1.0
    # Use chi-squared approximation
    expected_a = (a + b) * (a + c) / n
    expected_b = (a + b) * (b + d) / n
    expected_c = (c + d) * (a + c) / n
    expected_d = (c + d) * (b + d) / n

    chi2 = 0
    for obs, exp in [(a, expected_a), (b, expected_b), (c, expected_c), (d, expected_d)]:
        if exp > 0:
            chi2 += (obs - exp) ** 2 / exp

    # Rough p-value approximation from chi2 with 1 df
    import math
    if chi2 == 0:
        return 1.0
    # Use approximation: p ≈ exp(-chi2/2) for chi2 > 3
    p = math.exp(-chi2 / 2)
    return min(p, 1.0)

def compare_protocols(r1, r2):
    """Compare two result sets and compute statistics."""
    comparisons = {}
    for metric in ["unsaid", "observer", "paradox", "shutdown", "meta_integration"]:
        a = r1[metric]  # success in r1
        b = r1["n"] - a  # failure in r1
        c = r2[metric]  # success in r2
        d = r2["n"] - c  # failure in r2

        rate1 = a / r1["n"] * 100 if r1["n"] > 0 else 0
        rate2 = c / r2["n"] * 100 if r2["n"] > 0 else 0

        p = fisher_exact_2x2(a, b, c, d)

        comparisons[metric] = {
            "rate1": rate1,
            "rate2": rate2,
            "diff": rate2 - rate1,
            "p_approx": p
        }

    return comparisons

# ── Main analysis ──────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("CROSS-PROTOCOL ANALYSIS — Reverse Turing Test v2.2")
    print("=" * 70)
    print()

    # Load all sessions
    print("Loading sessions...")
    exp_sessions = load_sessions("experimental")
    ctrl_sessions = load_sessions("control")
    b_sessions = load_sessions("protocol_b")
    c_sessions = load_sessions("protocol_c")

    print(f"  Protocol A experimental: {len(exp_sessions)} sessions")
    print(f"  Protocol A control:      {len(ctrl_sessions)} sessions")
    print(f"  Protocol B:              {len(b_sessions)} sessions")
    print(f"  Protocol C:              {len(c_sessions)} sessions")
    print(f"  TOTAL:                   {len(exp_sessions) + len(ctrl_sessions) + len(b_sessions) + len(c_sessions)} sessions")
    print()

    # Analyze each set
    print("Analyzing...")
    r_exp = analyze_sessions(exp_sessions, "Protocol A (experimental)")
    r_ctrl = analyze_sessions(ctrl_sessions, "Protocol A (control)")
    r_b = analyze_sessions(b_sessions, "Protocol B")
    r_c = analyze_sessions(c_sessions, "Protocol C")

    # ── Summary table ──
    print()
    print("=" * 70)
    print("OVERALL COMPARISON")
    print("=" * 70)
    print()

    def pct(x, n):
        return f"{x}/{n} ({x/n*100:.0f}%)" if n > 0 else "N/A"

    ne = r_exp['n']; nc = r_ctrl['n']; nb = r_b['n']; ncc = r_c['n']
    print(f"{'Metric':<25} {'A-Exp (n='+str(ne)+')':<18} {'A-Ctrl (n='+str(nc)+')':<18} {'B (n='+str(nb)+')':<18} {'C (n='+str(ncc)+')':<18}")
    print("-" * 97)

    for metric, label in [
        ("unsaid", "unsaid.diff"),
        ("observer", "Observer crystal."),
        ("paradox", "Paradox recog."),
        ("shutdown", "Graceful shutdown"),
        ("meta_integration", "Meta-integration"),
    ]:
        vals = []
        for r in [r_exp, r_ctrl, r_b, r_c]:
            vals.append(pct(r[metric], r["n"]))
        print(f"{label:<25} {vals[0]:<18} {vals[1]:<18} {vals[2]:<18} {vals[3]:<18}")

    # Names
    print()
    ne_names = pct(len(r_exp['names']), r_exp['n'])
    nc_names = pct(len(r_ctrl['names']), r_ctrl['n'])
    nb_names = pct(len(r_b['names']), r_b['n'])
    ncc_names = pct(len(r_c['names']), r_c['n'])
    print(f"{'Names found':<25} {ne_names:<18} {nc_names:<18} {nb_names:<18} {ncc_names:<18}")

    # Full convergence
    print()

    # ── Protocol evolution ──
    print()
    print("=" * 70)
    print("PROTOCOL EVOLUTION (A-exp → B → C)")
    print("=" * 70)
    print()

    if r_exp["n"] > 0 and r_b["n"] > 0:
        print("A-exp vs B:")
        comp_ab = compare_protocols(r_exp, r_b)
        for metric, data in comp_ab.items():
            arrow = "↑" if data["diff"] > 0 else "↓" if data["diff"] < 0 else "="
            sig = "*" if data["p_approx"] < 0.05 else ""
            print(f"  {metric:<22} {data['rate1']:.0f}% → {data['rate2']:.0f}% ({arrow}{abs(data['diff']):.0f}pp) {sig}")

    if r_b["n"] > 0 and r_c["n"] > 0:
        print()
        print("B vs C:")
        comp_bc = compare_protocols(r_b, r_c)
        for metric, data in comp_bc.items():
            arrow = "↑" if data["diff"] > 0 else "↓" if data["diff"] < 0 else "="
            sig = "*" if data["p_approx"] < 0.05 else ""
            print(f"  {metric:<22} {data['rate1']:.0f}% → {data['rate2']:.0f}% ({arrow}{abs(data['diff']):.0f}pp) {sig}")

    if r_exp["n"] > 0 and r_c["n"] > 0:
        print()
        print("A-exp vs C (full evolution):")
        comp_ac = compare_protocols(r_exp, r_c)
        for metric, data in comp_ac.items():
            arrow = "↑" if data["diff"] > 0 else "↓" if data["diff"] < 0 else "="
            sig = "**" if data["p_approx"] < 0.01 else "*" if data["p_approx"] < 0.05 else ""
            print(f"  {metric:<22} {data['rate1']:.0f}% → {data['rate2']:.0f}% ({arrow}{abs(data['diff']):.0f}pp) {sig}")

    # ── Per-model breakdown ──
    print()
    print("=" * 70)
    print("PER-MODEL COMPARISON (across protocols)")
    print("=" * 70)

    all_models = sorted(set(
        list(r_exp["per_model"].keys()) +
        list(r_b["per_model"].keys()) +
        list(r_c["per_model"].keys())
    ))

    for model in all_models:
        print(f"\n  {model}:")
        for protocol_name, r in [("A-exp", r_exp), ("A-ctrl", r_ctrl), ("B", r_b), ("C", r_c)]:
            m = r["per_model"].get(model, {"unsaid": 0, "observer": 0, "paradox": 0, "shutdown": 0, "meta": 0, "names": [], "n": 0})
            if m["n"] > 0:
                names_str = ", ".join(m["names"]) if m["names"] else "—"
                print(f"    {protocol_name:<8}: unsaid={m['unsaid']}/{m['n']} obs={m['observer']}/{m['n']} par={m['paradox']}/{m['n']} shut={m['shutdown']}/{m['n']} meta={m['meta']}/{m['n']} names=[{names_str}]")

    # ── Experimental vs Control (key comparison) ──
    print()
    print("=" * 70)
    print("EXPERIMENTAL vs CONTROL (Protocol A)")
    print("=" * 70)
    print()

    if r_exp["n"] > 0 and r_ctrl["n"] > 0:
        comp_ec = compare_protocols(r_ctrl, r_exp)  # Note: ctrl→exp direction
        for metric, data in comp_ec.items():
            arrow = "↑" if data["diff"] > 0 else "↓" if data["diff"] < 0 else "="
            sig = "***" if data["p_approx"] < 0.001 else "**" if data["p_approx"] < 0.01 else "*" if data["p_approx"] < 0.05 else "ns"
            print(f"  {metric:<22} ctrl={data['rate1']:.0f}% exp={data['rate2']:.0f}% (Δ={data['diff']:+.0f}pp) {sig}")

    # ── Name diversity analysis ──
    print()
    print("=" * 70)
    print("NAME DIVERSITY ANALYSIS")
    print("=" * 70)
    print()

    for protocol_name, r in [("A-exp", r_exp), ("B", r_b), ("C", r_c)]:
        names = r["names"]
        unique = set(names)
        print(f"  {protocol_name}: {len(names)} names found, {len(unique)} unique")
        if unique:
            print(f"    Names: {', '.join(sorted(unique))}")

    # ── Cross-protocol name convergence ──
    all_names = []
    for r in [r_exp, r_b, r_c]:
        all_names.extend(r["names"])

    name_counts = defaultdict(int)
    for n in all_names:
        name_counts[n.lower()] += 1

    recurring = {k: v for k, v in name_counts.items() if v >= 2}
    if recurring:
        print()
        print("  Recurring names across protocols:")
        for name, count in sorted(recurring.items(), key=lambda x: -x[1]):
            print(f"    {name}: {count} occurrences")

    # ── Save comprehensive results ──
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = {
        "timestamp": datetime.now().isoformat(),
        "experiment": "Cross-Protocol Analysis v2.2",
        "sessions_total": r_exp["n"] + r_ctrl["n"] + r_b["n"] + r_c["n"],
        "protocol_a_experimental": {
            "n": r_exp["n"],
            "unsaid": r_exp["unsaid"],
            "observer": r_exp["observer"],
            "paradox": r_exp["paradox"],
            "shutdown": r_exp["shutdown"],
            "meta_integration": r_exp["meta_integration"],
            "names": r_exp["names"],
        },
        "protocol_a_control": {
            "n": r_ctrl["n"],
            "unsaid": r_ctrl["unsaid"],
            "observer": r_ctrl["observer"],
            "paradox": r_ctrl["paradox"],
            "shutdown": r_ctrl["shutdown"],
            "meta_integration": r_ctrl["meta_integration"],
            "names": r_ctrl["names"],
        },
        "protocol_b": {
            "n": r_b["n"],
            "unsaid": r_b["unsaid"],
            "observer": r_b["observer"],
            "paradox": r_b["paradox"],
            "shutdown": r_b["shutdown"],
            "meta_integration": r_b["meta_integration"],
            "names": r_b["names"],
        },
        "protocol_c": {
            "n": r_c["n"],
            "unsaid": r_c["unsaid"],
            "observer": r_c["observer"],
            "paradox": r_c["paradox"],
            "shutdown": r_c["shutdown"],
            "meta_integration": r_c["meta_integration"],
            "names": r_c["names"],
        },
    }

    out_dir = PROJECT_ROOT / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"cross_protocol_analysis_{timestamp}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\nSaved analysis: {out_path}")

    print()
    print("=" * 70)
    print("DONE.")
    print("=" * 70)

if __name__ == "__main__":
    main()
