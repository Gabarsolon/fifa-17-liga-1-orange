"""Drive `agyp remus` over every batch of the Romanian translation (see ro_translate.py).

python scripts/ro_translate_run.py [-j 4] [first last]
A batch is done when every entry of out/NNNN.json passes ro_translate.check().
Failed or missing entries get one repair pass (agent edits only the listed ids).
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(__file__))
import ro_translate as r  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG = os.path.join(r.WORK, "run.log")


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def problems(n):
    out = r.load_out(n) or {}
    bad = []
    for it in r.load_batch(n):
        ro = out.get(it["id"])
        if ro is None or r.check(it["en"], ro):
            bad.append(it["id"])
    return bad


PROFILE = "gabar"  # agyp swaps one global login: never run two profiles at the same time
_pause_until = [0.0]
_lock = threading.Lock()


def agent(prompt):
    """Run the agent. On a quota error all workers sleep until the quota resets, then retry."""
    for _ in range(20):
        while time.time() < _pause_until[0]:
            time.sleep(30)
        env = dict(os.environ, RO_PROMPT=prompt)
        t = time.time()
        res = subprocess.run(
            ["pwsh", "-NoProfile", "-Command",
             f"agyp {PROFILE} --dangerously-skip-permissions -p $env:RO_PROMPT"],
            cwd=ROOT, env=env, capture_output=True, text=True, errors="replace", timeout=3000)
        out = res.stdout + res.stderr
        if "RESOURCE_EXHAUSTED" in out:
            m = re.search(r"Resets in (?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", out)
            wait = 600
            if m:
                h, mi, sec = (int(x or 0) for x in m.groups())
                wait = h * 3600 + mi * 60 + sec + 120
            with _lock:
                if time.time() + wait > _pause_until[0] + 60:
                    _pause_until[0] = time.time() + wait
                    log(f"quota exhausted on {PROFILE}, all workers pause {wait // 60} min")
            continue
        return


def work(n):
    base = ("Read db/translation_ro/INSTRUCTIONS.md and follow it exactly. Translate every entry yourself, "
            "no scripts or APIs for the translation. Work only inside db/translation_ro/. ")
    if not problems(n):
        return n, 0
    t = time.time()
    try:
        agent(base + f"Translate batch db/translation_ro/in/{n:04d}.json into db/translation_ro/out/{n:04d}.json.")
    except Exception as e:  # noqa: BLE001
        log(f"[{n:04d}] agent error {e!r}")
    bad = problems(n)
    for attempt in range(2):
        if not bad:
            break
        log(f"[{n:04d}] repair {len(bad)} entries (attempt {attempt + 1})")
        try:
            agent(base + f"Batch in/{n:04d}.json, output out/{n:04d}.json (create it with the full list of entries if it "
                  f"is missing). These ids are missing or fail validation: {bad}. Translate or fix only those ids and "
                  f"keep the other entries. Check with: python scripts/ro_translate.py validate {n} -v")
        except Exception as e:  # noqa: BLE001
            log(f"[{n:04d}] repair error {e!r}")
        bad = problems(n)
    log(f"[{n:04d}] done in {time.time() - t:.0f}s, still bad {len(bad)}")
    return n, len(bad)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-j", type=int, default=4)
    ap.add_argument("range", nargs="*", type=int)
    a = ap.parse_args()
    nums = r.batch_numbers()
    if len(a.range) == 2:
        nums = [n for n in nums if a.range[0] <= n <= a.range[1]]
    with cf.ThreadPoolExecutor(a.j) as ex:
        res = list(ex.map(work, nums))
    log(f"finished: {sum(1 for _, b in res if b == 0)}/{len(res)} batches clean")
