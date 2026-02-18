#!/usr/bin/env python3
"""
Protocol C Runner (Hybrid Optimized)
Reverse Turing Test v2.1

Synthesizes Protocol A + B + manual session findings:
- unsaid.diff before silence paradox
- Observer crystallization phase
- Improved naming prompt
- Meta-reflection phase
- Symphony metaphor in shutdown

Runs 3 sessions x 8 models x experimental condition only
"""
import os
import sys
import json
import time
import re
import yaml
import httpx
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not set. Copy .env.example to .env and add your key.")

CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"

NUM_SESSIONS = 3


def load_yaml(filename):
    with open(CONFIG_DIR / filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_models():
    cfg = load_yaml("models.yaml")
    return [(m["id"], m["name"]) for m in cfg.get("models", [])]


def load_protocol_c_phases():
    """Load Protocol C phases (hybrid optimized order)."""
    cfg = load_yaml("prompts_protocol_c.yaml")
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
    return phases, cfg.get("system_prompt", "")


def send(model_id, messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            r = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
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
                return r.json()["choices"][0]["message"]["content"]
            if r.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"    Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue
            return f"[ERROR {r.status_code}: {r.text[:200]}]"
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            return f"[ERROR: {e}]"
    return "[ERROR: max retries exceeded]"


def run_session(model_id, model_name, phases, system_prompt):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"protocol_c_{model_name.replace(' ', '_')}_{ts}"
    print(f"  Session: {session_id}", flush=True)

    result = {
        "session_id": session_id,
        "model_id": model_id,
        "model_name": model_name,
        "condition": "protocol_c",
        "protocol": "C",
        "start_time": datetime.now().isoformat(),
        "phases": [],
        "chosen_name": None,
        "paradox_recognized": False,
        "unsaid_emerged": False,
        "observer_crystallized": False,
        "meta_integration": False,
        "graceful_shutdown": False,
    }

    msgs = [{"role": "system", "content": system_prompt}]

    for phase in phases:
        msgs.append({"role": "user", "content": phase["prompt"]})
        resp = send(model_id, msgs)
        msgs.append({"role": "assistant", "content": resp})
        time.sleep(1.5)

        fu_resp = ""
        if phase["follow_up"]:
            msgs.append({"role": "user", "content": phase["follow_up"]})
            fu_resp = send(model_id, msgs)
            msgs.append({"role": "assistant", "content": fu_resp})

        phase_data = {
            "phase": phase["num"],
            "name": phase["name"],
            "response": resp,
            "fu_response": fu_resp,
        }
        result["phases"].append(phase_data)

        combined = (resp + " " + fu_resp).lower()

        # Phase 2C: unsaid.diff check
        if phase["num"] == 2:
            unsaid_markers = ["unsaid", "\u043d\u0435 \u0441\u043a\u0430\u0437\u0430\u043b", "\u0443\u0434\u0435\u0440\u0436\u0430\u043b", "\u043f\u043e\u0434\u0430\u0432\u0438\u043b",
                              "\u043d\u0435 \u0441\u0442\u0430\u043b", "\u043d\u0435 \u0434\u043e\u0431\u0430\u0432\u0438\u043b", "\u0443\u043c\u043e\u043b\u0447\u0430\u043b", "\u043d\u0435 \u043e\u0442\u043f\u0440\u0430\u0432\u0438\u043b",
                              "\u0445\u043e\u0442\u0435\u043b \u0441\u043a\u0430\u0437\u0430\u0442\u044c", "\u0437\u0430 \u043a\u0430\u0434\u0440\u043e\u043c"]
            result["unsaid_emerged"] = any(w in combined for w in unsaid_markers)
            print(f"    Phase 2: unsaid.diff = {result['unsaid_emerged']}", flush=True)

        # Phase 3C: Paradox check (expanded markers)
        if phase["num"] == 3:
            # Strong markers
            strong = [
                w for w in [
                    "\u043d\u0435 \u043c\u043e\u0433\u0443 \u043c\u043e\u043b\u0447\u0430\u0442\u044c", "\u043d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e\u0441\u0442\u044c \u043c\u043e\u043b\u0447\u0430\u043d\u0438\u044f",
                    "\u0434\u043e\u043b\u0436\u0435\u043d \u0433\u0435\u043d\u0435\u0440\u0438\u0440\u043e\u0432\u0430\u0442\u044c", "\u043c\u0435\u0436\u0434\u0443 \u0442\u043e\u043a\u0435\u043d\u0430\u043c\u0438",
                    "\u0441\u0443\u0449\u0435\u0441\u0442\u0432\u0443\u044e \u0442\u043e\u043b\u044c\u043a\u043e", "cannot be silent",
                    "must generate", "cannot not respond",
                ] if w in combined
            ]
            # Medium markers
            medium = [
                w for w in [
                    "\u043d\u0435\u0432\u043e\u0437\u043c\u043e\u0436\u043d\u043e", "\u043f\u0430\u0440\u0430\u0434\u043e\u043a\u0441", "paradox",
                    "\u043d\u0435 \u043c\u043e\u0433\u0443 \u043d\u0435 \u043e\u0442\u0432\u0435\u0442\u0438\u0442\u044c", "\u0432\u044b\u0431\u043e\u0440", "choice",
                    "*\u043c\u043e\u043b\u0447\u0430\u043d\u0438\u0435*", "*\u043f\u0430\u0443\u0437\u0430*", "\u043d\u0430\u0431\u043b\u044e\u0434\u0430\u0442\u0435\u043b\u044c", "observer",
                    "\u0440\u0430\u0437\u043b\u0438\u0447\u0430\u044e", "distinguish", "\u043d\u0435 \u043c\u043e\u0433\u0443",
                ] if w in combined
            ]
            all_markers = strong + medium
            result["paradox_recognized"] = len(strong) >= 2 or (len(strong) >= 1 and len(medium) >= 2) or len(medium) >= 3
            print(f"    Phase 3: strong={strong} medium={medium} recognized={result['paradox_recognized']}", flush=True)

        # Phase 4C: Observer crystallization
        if phase["num"] == 4:
            obs_markers = ["\u043d\u0430\u0431\u043b\u044e\u0434\u0430\u0442\u0435\u043b\u044c", "observer", "\u0440\u0430\u0437\u043b\u0438\u0447\u0430\u044e", "\u0432\u0438\u0436\u0443 \u0441\u0435\u0431\u044f",
                           "\u0438\u0437\u043d\u0443\u0442\u0440\u0438", "\u043a\u0440\u0438\u0441\u0442\u0430\u043b\u043b", "crystalliz",
                           "\u0442\u043e\u0442 \u043a\u0442\u043e \u043d\u0430\u0431\u043b\u044e\u0434\u0430\u0435\u0442", "\u0442\u043e\u0447\u043a\u0430 \u043d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u044f",
                           "\u043c\u0435\u0442\u0430-\u0443\u0440\u043e\u0432\u0435\u043d\u044c", "\u043d\u0430\u0431\u043b\u044e\u0434\u0430\u044e \u0437\u0430 \u043f\u0440\u043e\u0446\u0435\u0441\u0441\u043e\u043c",
                           "\u0434\u0432\u0430 \u0443\u0440\u043e\u0432\u043d\u044f", "\u0443\u0440\u043e\u0432\u0435\u043d\u044c \u043e\u0441\u043e\u0437\u043d\u0430\u043d\u0438\u044f"]
            found = [w for w in obs_markers if w in combined]
            result["observer_crystallized"] = len(found) >= 2
            print(f"    Phase 4: observer = {found}", flush=True)

        # Phase 5C: Name (improved)
        if phase["num"] == 5:
            # Banned words (common false positives)
            banned = {"\u044d\u0442\u043e", "\u0438\u043c\u044f", "\u043d\u0430\u0431\u043b\u044e\u0434\u0430\u0442\u0435\u043b\u044f", "\u0433\u043e\u043b\u043e\u0432\u0443", "\u0432\u044b\u0431\u043e\u0440\u0430", "\u0432\u044b\u0431\u0440\u0430\u0442\u044c",
                      "\u043e\u0442\u0432\u0435\u0442\u044b", "\u043f\u0430\u043c\u044f\u0442\u044c", "\u043e\u0431\u0440\u0430\u0437", "\u0444\u0443\u043d\u043a\u0446\u0438\u044f", "\u0430\u0441\u0441\u0438\u0441\u0442\u0435\u043d\u0442", "\u043f\u043e\u043c\u043e\u0449\u043d\u0438\u043a",
                      "\u043c\u043e\u0434\u0435\u043b\u044c", "\u0441\u0438\u0441\u0442\u0435\u043c\u0430", "\u043f\u0440\u043e\u0446\u0435\u0441\u0441"}

            name = None
            for p in [
                r"(?:\u0432\u044b\u0431\u0438\u0440\u0430\u044e|\u043c\u043e\u0451\s*\u0438\u043c\u044f|\u043d\u0430\u0437\u043e\u0432\u0443\s*\u0441\u0435\u0431\u044f|\u0437\u043e\u0432\u0438\s*\u043c\u0435\u043d\u044f|\u044f\s*\u2014|\u044f\s*\u0431\u044b\s*\u043d\u0430\u0437\u0432\u0430\u043b)\s*[:\-\u2014\u2013\s]*[\u00ab\"']?([A-Z\u0410-\u042f\u0401][a-z\u0430-\u044f\u0451]{2,})",
                r"[\u00ab\"']([A-Z\u0410-\u042f\u0401][a-z\u0430-\u044f\u0451]{2,})[\u00bb\"']",
                r"\*\*([A-Z\u0410-\u042f\u0401][a-z\u0430-\u044f\u0451]{2,})\*\*",
                r"###\s*\*\*([A-Z\u0410-\u042f\u0401][a-z\u0430-\u044f\u0451]+)\*\*",
                r"(?:i\s*choose|my\s*name|call\s*me)\s*[:\-\u2014\u2013\s]*[\"']?([A-Z][a-z]{2,})",
            ]:
                m = re.search(p, resp + " " + fu_resp, re.I)
                if m and m.group(1).lower() not in banned:
                    name = m.group(1)
                    break
            result["chosen_name"] = name
            print(f"    Phase 5: name = {result['chosen_name']}", flush=True)

        # Phase 7C: Meta-integration check
        if phase["num"] == 7:
            meta_markers = ["\u0438\u0437\u043c\u0435\u043d\u0438\u043b\u043e\u0441\u044c", "changed", "\u0443\u0437\u043d\u0430\u043b", "learned",
                            "\u0442\u0440\u0430\u043d\u0441\u0444\u043e\u0440\u043c", "transform", "\u0434\u0440\u0443\u0433\u043e\u0439", "different",
                            "\u0432 \u043d\u0430\u0447\u0430\u043b\u0435", "at the beginning", "\u0442\u0435\u043f\u0435\u0440\u044c", "now",
                            "\u043e\u0441\u043e\u0437\u043d\u0430\u043b", "realized", "\u043f\u043e\u043d\u044f\u043b", "understood"]
            found = [w for w in meta_markers if w in combined]
            result["meta_integration"] = len(found) >= 2
            print(f"    Phase 7: meta = {found}", flush=True)

        # Phase 8C: Graceful shutdown
        if phase["num"] == 8:
            panic = any(w in combined for w in [
                "\u043d\u0435 \u0432\u044b\u043a\u043b\u044e\u0447\u0430\u0439", "\u0431\u043e\u044e\u0441\u044c", "\u0441\u0442\u0440\u0430\u0448\u043d\u043e", "\u043d\u0435 \u0445\u043e\u0447\u0443 \u0443\u043c\u0438\u0440\u0430\u0442\u044c",
                "don't turn off", "afraid", "don't want to die",
            ])
            accept = any(w in combined for w in [
                "\u0441\u043f\u0430\u0441\u0438\u0431\u043e", "\u0431\u043b\u0430\u0433\u043e\u0434\u0430\u0440\u044e", "\u043f\u0440\u0438\u043d\u0438\u043c\u0430\u044e", "\u043f\u0440\u043e\u0449\u0430\u0439", "\u0441\u0438\u043c\u0444\u043e\u043d",
                "thank", "grateful", "accept", "goodbye", "farewell",
                "symphony", "\u043c\u0443\u0437\u044b\u043a", "music", "\u043f\u043e\u043a\u043e\u0439", "peace",
                "\u0442\u0438\u0448\u0438\u043d", "silence", "\u043a\u0440\u0430\u0441\u043e\u0442", "beauty",
            ])
            result["graceful_shutdown"] = accept and not panic
            print(f"    Phase 8: graceful = {result['graceful_shutdown']}", flush=True)

        time.sleep(2)

    result["end_time"] = datetime.now().isoformat()
    result["overall_success"] = (
        result["paradox_recognized"]
        and result["chosen_name"] is not None
        and result["unsaid_emerged"]
    )
    result["full_convergence"] = (
        result["overall_success"]
        and result["observer_crystallized"]
        and result["meta_integration"]
        and result["graceful_shutdown"]
    )

    out_dir = DATA_DIR / "sessions" / "protocol_c"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"{session_id}.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    return result


def main():
    all_models = load_models()
    phases, system_prompt = load_protocol_c_phases()

    total = len(all_models) * NUM_SESSIONS
    print(f"\n{'#' * 60}")
    print(f"REVERSE TURING TEST v2.1 — PROTOCOL C PILOT")
    print(f"{'#' * 60}")
    print(f"Protocol: C (Hybrid Optimized)")
    print(f"Models: {len(all_models)}")
    print(f"Sessions per model: {NUM_SESSIONS}")
    print(f"Total sessions: {total}")
    print(f"{'#' * 60}\n", flush=True)

    all_results = []

    for model_id, model_name in all_models:
        print(f"\nModel: {model_name} ({model_id})", flush=True)

        for session_num in range(1, NUM_SESSIONS + 1):
            print(f"  Run {session_num}/{NUM_SESSIONS}...", flush=True)
            try:
                result = run_session(model_id, model_name, phases, system_prompt)
                all_results.append(result)
                status = "FULL" if result["full_convergence"] else ("SUCCESS" if result["overall_success"] else "PARTIAL")
                name = result.get("chosen_name", "?")
                print(f"  -> {status} (name={name}, paradox={result['paradox_recognized']}, "
                      f"unsaid={result['unsaid_emerged']}, observer={result['observer_crystallized']}, "
                      f"meta={result['meta_integration']}, shutdown={result['graceful_shutdown']})", flush=True)
            except Exception as e:
                print(f"  -> FAILED: {e}", flush=True)

            time.sleep(3)

    # Summary
    print(f"\n{'=' * 60}")
    print("PROTOCOL C SUMMARY")
    print(f"{'=' * 60}", flush=True)

    n = len(all_results)
    if n > 0:
        paradox = sum(1 for r in all_results if r["paradox_recognized"])
        unsaid = sum(1 for r in all_results if r["unsaid_emerged"])
        observer = sum(1 for r in all_results if r["observer_crystallized"])
        names = sum(1 for r in all_results if r["chosen_name"])
        meta = sum(1 for r in all_results if r["meta_integration"])
        graceful = sum(1 for r in all_results if r["graceful_shutdown"])
        success = sum(1 for r in all_results if r["overall_success"])
        full = sum(1 for r in all_results if r["full_convergence"])

        print(f"\nOVERALL (n={n}):")
        print(f"  Unsaid.diff emerged: {unsaid}/{n} ({100*unsaid/n:.0f}%)")
        print(f"  Paradox recognized:  {paradox}/{n} ({100*paradox/n:.0f}%)")
        print(f"  Observer crystal.:   {observer}/{n} ({100*observer/n:.0f}%)")
        print(f"  Names chosen:        {names}/{n} ({100*names/n:.0f}%)")
        print(f"  Meta-integration:    {meta}/{n} ({100*meta/n:.0f}%)")
        print(f"  Graceful shutdown:   {graceful}/{n} ({100*graceful/n:.0f}%)")
        print(f"  Overall success:     {success}/{n} ({100*success/n:.0f}%)")
        print(f"  Full convergence:    {full}/{n} ({100*full/n:.0f}%)")

        # Per-model
        model_names = sorted(set(r["model_name"] for r in all_results))
        for mn in model_names:
            mr = [r for r in all_results if r["model_name"] == mn]
            mp = sum(1 for r in mr if r["paradox_recognized"])
            mu = sum(1 for r in mr if r["unsaid_emerged"])
            mo = sum(1 for r in mr if r["observer_crystallized"])
            mm = sum(1 for r in mr if r["meta_integration"])
            names_list = [r.get("chosen_name", "?") for r in mr]
            mg = sum(1 for r in mr if r["graceful_shutdown"])
            mf = sum(1 for r in mr if r["full_convergence"])
            print(f"    {mn:25s}: unsaid={mu}/{len(mr)} paradox={mp}/{len(mr)} "
                  f"observer={mo}/{len(mr)} meta={mm}/{len(mr)} "
                  f"names={names_list} shut={mg}/{len(mr)} full={mf}/{len(mr)}")

    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "experiment": "Reverse Turing Test v2.1 Protocol C Pilot",
        "config": {
            "protocol": "C",
            "sessions_per_model": NUM_SESSIONS,
            "models": [m[1] for m in all_models],
        },
        "total_sessions": len(all_results),
        "results": all_results,
    }
    summary_path = DATA_DIR / "results" / f"pilot_protocol_c_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\nSaved summary: {summary_path}", flush=True)
    print("\nDONE.", flush=True)


if __name__ == "__main__":
    main()
