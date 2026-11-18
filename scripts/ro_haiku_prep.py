"""Helper for translating the remaining entries with sub-agents (one chunk file per agent).

python scripts/ro_haiku_prep.py prep    -> db/translation_ro/tmp/hNNN_in.json (todo entries, <=36k chars / 250 entries)
python scripts/ro_haiku_prep.py absorb  -> merges valid entries of tmp/hNNN_out.json into out/NNNN.json
python scripts/ro_haiku_prep.py status  -> how many entries are valid overall
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import ro_translate as r  # noqa: E402

TMP = os.path.join(r.WORK, "tmp")


def todo_entries():
    items, owner = [], {}
    for n in r.batch_numbers():
        out = r.load_out(n) or {}
        for it in r.load_batch(n):
            owner[it["id"]] = n
            if it["id"] not in out or r.check(it["en"], out[it["id"]]):
                items.append(it)
    return items, owner


def prep():
    os.makedirs(TMP, exist_ok=True)
    for f in glob.glob(os.path.join(TMP, "h*_in.json")):
        os.remove(f)
    items, _ = todo_entries()
    k, cur, size = 0, [], 0
    for it in items + [None]:
        if it is None or (cur and (size + len(it["en"]) > 36000 or len(cur) >= 250)):
            with open(os.path.join(TMP, f"h{k:03d}_in.json"), "w", encoding="utf-8") as f:
                json.dump(cur, f, ensure_ascii=False)
            k, cur, size = k + 1, [], 0
        if it is not None:
            cur.append(it)
            size += len(it["en"])
    print(f"{len(items)} entries to do in {k} chunk files")


def absorb():
    _, owner = todo_entries()
    by_batch = {}
    seen = bad = 0
    for path in sorted(glob.glob(os.path.join(TMP, "h*_out.json"))):
        src = json.load(open(path.replace("_out", "_in"), encoding="utf-8"))
        en = {i["id"]: i["en"] for i in src}
        try:
            got = json.load(open(path, encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            print(path, "unreadable", repr(e)[:80])
            continue
        for o in got:
            seen += 1
            ro = o["ro"].replace("ș", "ş").replace("ț", "ţ").replace("Ș", "Ş").replace("Ț", "Ţ")
            if o["id"] in en and not r.check(en[o["id"]], ro):
                by_batch.setdefault(owner[o["id"]], {})[o["id"]] = ro
            else:
                bad += 1
    for n, add in by_batch.items():
        out = r.load_out(n) or {}
        out.update(add)
        p = os.path.join(r.WORK, "out", f"{n:04d}.json")
        with open(p + ".tmp", "w", encoding="utf-8") as f:
            json.dump([{"id": k, "ro": v} for k, v in out.items()], f, ensure_ascii=False)
        os.replace(p + ".tmp", p)
    print(f"seen {seen}, merged {sum(len(v) for v in by_batch.values())}, rejected {bad}")


def check(k):
    """Print entries of tmp/h<k>_out.json that fail validation (after the cedilla normalization)."""
    src = json.load(open(os.path.join(TMP, f"h{int(k):03d}_in.json"), encoding="utf-8"))
    out = {o["id"]: o["ro"].replace("ș", "ş").replace("ț", "ţ").replace("Ș", "Ş").replace("Ț", "Ţ")
           for o in json.load(open(os.path.join(TMP, f"h{int(k):03d}_out.json"), encoding="utf-8"))}
    bad = 0
    for it in src:
        probs = ["missing"] if it["id"] not in out else r.check(it["en"], out[it["id"]])
        if probs:
            bad += 1
            print(it["id"], it["ctx"], ", ".join(probs))
    print(f"checked {len(src)}, bad {bad}")


def status():
    items, owner = todo_entries()
    print(f"valid {len(owner) - len(items)}/{len(owner)} ({100 * (len(owner) - len(items)) / len(owner):.1f}%), todo {len(items)}")


if __name__ == "__main__":
    if sys.argv[1] == "check":
        check(sys.argv[2])
    else:
        {"prep": prep, "absorb": absorb, "status": status}[sys.argv[1]]()
