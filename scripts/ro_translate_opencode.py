"""Translate the batches of ro_translate.py with free models through `opencode run`.

python scripts/ro_translate_opencode.py [-j 3] [-m provider/model ...] [first last]

Per batch: the entries that are missing or fail ro_translate.check() are sent in chunks
(max 60 entries / 9000 chars) together with INSTRUCTIONS.md; the model answers with a JSON array,
the script normalizes comma-below letters to cedilla, validates every entry and saves only valid
ones to out/NNNN.json. Entries that still fail are retried with the next model of the list.
"""
import argparse
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
import ro_translate as r  # noqa: E402

LOG = os.path.join(r.WORK, "run.log")
INSTR = os.path.join(r.WORK, "INSTRUCTIONS.md")
TMP = os.path.join(r.WORK, "tmp")
MODELS = ["opencode/deepseek-v4.1-flash-free", "opencode/mimo-v2.6-flash-free"]
ANSI = re.compile(r"\x1b\[[0-9;]*m")
MSG = ("Follow the attached INSTRUCTIONS.md exactly. Translate every entry of the attached chunk file "
       "into Romanian. Do not use tools and do not write files. Reply with ONLY a JSON array "
       '[{"id": <id>, "ro": "<translation>"}] with all ids, no markdown fences, no commentary. '
       "Use cedilla letters only (ş ţ). Keep every token and every club name exactly.")


def log(msg):
    line = time.strftime("%H:%M:%S ") + msg
    print(line, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def norm(s):
    return s.replace("ș", "ş").replace("ț", "ţ").replace("Ș", "Ş").replace("Ț", "Ţ")


def chunks(items, max_n=60, max_chars=9000):
    cur, size = [], 0
    for it in items:
        if cur and (len(cur) >= max_n or size + len(it["en"]) > max_chars):
            yield cur
            cur, size = [], 0
        cur.append(it)
        size += len(it["en"])
    if cur:
        yield cur


def ask(model, path):
    p = subprocess.run(
        ["opencode", "run", "-m", model, "-f", INSTR, "-f", path, MSG],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=720, stdin=subprocess.DEVNULL)
    txt = ANSI.sub("", p.stdout)
    a, b = txt.find("["), txt.rfind("]")
    if a < 0 or b < a:
        raise ValueError("no JSON array: " + (txt + p.stderr)[-150:].replace("\n", " "))
    return {o["id"]: norm(o["ro"]) for o in json.loads(txt[a:b + 1])}


def save(n, out):
    path = os.path.join(r.WORK, "out", f"{n:04d}.json")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump([{"id": k, "ro": v} for k, v in out.items()], f, ensure_ascii=False)
    os.replace(path + ".tmp", path)


def work(n, models):
    t = time.time()
    batch = r.load_batch(n)
    out = r.load_out(n) or {}
    out = {k: v for k, v in out.items() if k in {i["id"] for i in batch}}
    for model in models:
        todo = [i for i in batch if i["id"] not in out or r.check(i["en"], out[i["id"]])]
        if not todo:
            break
        for k, ch in enumerate(chunks(todo)):
            path = os.path.join(TMP, f"{n:04d}_{k:02d}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(ch, f, ensure_ascii=False)
            try:
                got = ask(model, path)
            except Exception as e:  # noqa: BLE001
                log(f"[{n:04d}] {model} chunk {k} failed: {repr(e)[:160]}")
                continue
            good = 0
            for it in ch:
                ro = got.get(it["id"])
                if ro is not None and not r.check(it["en"], ro):
                    out[it["id"]] = ro
                    good += 1
            save(n, out)
            log(f"[{n:04d}] {model} chunk {k}: {good}/{len(ch)} valid")
    bad = [i["id"] for i in batch if i["id"] not in out or r.check(i["en"], out[i["id"]])]
    log(f"[{n:04d}] done in {time.time() - t:.0f}s, still bad {len(bad)}")
    return n, len(bad)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-j", type=int, default=3)
    ap.add_argument("-m", action="append", dest="models")
    ap.add_argument("range", nargs="*", type=int)
    a = ap.parse_args()
    os.makedirs(TMP, exist_ok=True)
    nums = r.batch_numbers()
    if len(a.range) == 2:
        nums = [n for n in nums if a.range[0] <= n <= a.range[1]]
    models = a.models or MODELS
    todo = [n for n in nums if any(i["id"] not in (r.load_out(n) or {}) or
                                   r.check(i["en"], (r.load_out(n) or {}).get(i["id"], ""))
                                   for i in r.load_batch(n))]
    log(f"opencode run: {len(todo)} batches to do, models {models}")
    with cf.ThreadPoolExecutor(a.j) as ex:
        res = list(ex.map(lambda n: work(n, models), todo))
    log(f"finished: {sum(1 for _, b in res if b == 0)}/{len(res)} batches clean")
