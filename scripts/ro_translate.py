"""Romanian translation pipeline for db/LanguageStrings.txt (issue #6).

prepare  -> db/translation_ro/in/NNNN.json   (unique texts, batches for an LLM)
validate -> checks db/translation_ro/out/NNNN.json against its input batch
merge    -> db/LanguageStrings.ro.txt        (same format, translated where valid)

Batch in : [{"id": 12, "ctx": "news_title_x_1", "en": "..."}]
Batch out: [{"id": 12, "ro": "..."}]
"""
import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "db", "LanguageStrings.txt")
OUT_TXT = os.path.join(ROOT, "db", "LanguageStrings.ro.txt")
WORK = os.path.join(ROOT, "db", "translation_ro")
BATCH_CHARS = 40000
BATCH_MAX_ROWS = 250

# Name tables are not translated (team, city, nation, trophy, league, stadium names).
SKIP_ID = re.compile(
    r"^(CT_)?(TeamName|CityName|NationName|TrophyName|LeagueName|StadiumName)"
    r"|^FrostbiteOpenSourceCredits", re.I)
# Everything the game substitutes or interprets; must survive unchanged and in order.
TOKEN = re.compile(r"<[^<>\s][^<>]*>|%\d+|\{C:[^}]*\}|\{[\d.\-]+\}|\\[rn]")


def read_rows(path):
    text = open(path, encoding="utf-16-le", newline="").read().lstrip("﻿")
    lines = text.split("\r\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [l.split("\t") for l in lines]


_TEAM_NAMES = None
# Entries of the team table that are ordinary words or FUT/UI terms, not clubs.
GENERIC_TEAM_WORDS = {
    "ultimate team", "adidas", "team of the week", "central", "victory", "classic", "united",
    "champions", "fut team", "free agents", "all star", "legends", "world xi", "sporting",
    "palace", "eagles", "galaxy", "canaries", "racing", "nacional", "rangers", "colorado",
}


def team_names():
    """Club names from the name tables; they must stay literal in translations."""
    global _TEAM_NAMES
    if _TEAM_NAMES is None:
        names = set()
        rows = read_rows(SRC)[1:]
        nations = {t for t, _h, sid in rows if re.match(r"^(CT_)?NationName", sid)}
        for text, _h, sid in rows:
            if re.match(r"^(TeamName_\d+|TeamName_Abbr(10|15)_\d+|CT_TeamName_\d+)$", sid):
                text = text.strip()
                if text in nations or text.lower() in GENERIC_TEAM_WORDS:
                    continue
                if len(text) >= 6 or " " in text:
                    names.add(text)
        _TEAM_NAMES = sorted(names, key=len, reverse=True)
    return _TEAM_NAMES


def translatable(text, stringid):
    if SKIP_ID.match(stringid):
        return False
    stripped = TOKEN.sub("", text)
    return re.search(r"[A-Za-z]{2,}", stripped) is not None


def unique_texts(rows):
    seen = collections.OrderedDict()
    for text, _hash, sid in rows[1:]:
        if translatable(text, sid) and text not in seen:
            seen[text] = sid
    return seen


def cmd_prepare(args):
    out_dir = os.path.join(WORK, "out")
    if os.path.isdir(out_dir) and os.listdir(out_dir) and not args.force:
        sys.exit("out/ has translations and ids would shift: use --force (then remap outputs)")
    rows = read_rows(SRC)
    uniq = unique_texts(rows)
    os.makedirs(os.path.join(WORK, "in"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "out"), exist_ok=True)
    # Sort by length so batches of short strings and long news bodies stay apart.
    items = sorted(uniq.items(), key=lambda kv: len(kv[0]))
    batches, cur, chars = [], [], 0
    for i, (text, sid) in enumerate(items):
        if cur and (chars + len(text) > BATCH_CHARS or len(cur) >= BATCH_MAX_ROWS):
            batches.append(cur)
            cur, chars = [], 0
        cur.append({"id": i, "ctx": sid, "en": text})
        chars += len(text)
    if cur:
        batches.append(cur)
    for n, b in enumerate(batches):
        with open(os.path.join(WORK, "in", f"{n:04d}.json"), "w", encoding="utf-8") as f:
            json.dump(b, f, ensure_ascii=False, indent=0)
    print(f"rows {len(rows) - 1}, unique translatable texts {len(items)}, batches {len(batches)}")


def check(en, ro):
    """Return a list of problems with translation `ro` of `en`."""
    problems = []
    if collections.Counter(TOKEN.findall(en)) != collections.Counter(TOKEN.findall(ro)):
        problems.append("tokens differ")
    elif TOKEN.findall(en) != TOKEN.findall(ro) and "{C:" in en:
        problems.append("token order differs")
    if "\t" in ro or "\r" in ro or "\n" in ro:
        problems.append("real tab/newline")
    if en.startswith('"') != ro.startswith('"') or en.endswith('"') != ro.endswith('"'):
        problems.append("outer quotes differ")
    if len(ro) > 3 * len(en) + 20:
        problems.append("too long")
    if not ro.strip():
        problems.append("empty")
    if re.search(r"[șțȘȚ]", ro):
        problems.append("comma-below letter (use cedilla ş ţ)")
    if re.search(r"<[^<>]*\s>|<\s", ro):
        problems.append("space inside <>")
    for name in team_names():
        if name in en and re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", en) and name not in ro:
            problems.append(f"team name changed: {name}")
            break
    return problems


def load_batch(n):
    with open(os.path.join(WORK, "in", f"{n:04d}.json"), encoding="utf-8") as f:
        return json.load(f)


def load_out(n):
    p = os.path.join(WORK, "out", f"{n:04d}.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return {o["id"]: o["ro"] for o in json.load(f)}


def batch_numbers():
    return sorted(int(f[:4]) for f in os.listdir(os.path.join(WORK, "in")))


def cmd_validate(args):
    total = bad = missing = 0
    for n in args.batch if args.batch else batch_numbers():
        out = load_out(n)
        if out is None:
            continue
        for item in load_batch(n):
            total += 1
            if item["id"] not in out:
                missing += 1
                print(f"[{n:04d}] id {item['id']} missing")
                continue
            probs = check(item["en"], out[item["id"]])
            if probs:
                bad += 1
                print(f"[{n:04d}] id {item['id']} {item['ctx']}: {', '.join(probs)}")
                if args.verbose:
                    print("   EN:", item["en"][:200])
                    print("   RO:", out[item["id"]][:200])
    print(f"checked {total}, bad {bad}, missing {missing}")
    return 1 if bad or missing else 0


def cmd_merge(_args):
    rows = read_rows(SRC)
    en_to_ro = {}
    for n in batch_numbers():
        out = load_out(n)
        if out is None:
            continue
        for item in load_batch(n):
            ro = out.get(item["id"])
            if ro is not None and not check(item["en"], ro):
                en_to_ro[item["en"]] = ro
    done = 0
    # Per-stringid manual texts that win over the translation (e.g. the UI language entry shows "Română")
    ov_path = os.path.join(WORK, "overrides.json")
    overrides = json.load(open(ov_path, encoding="utf-8")) if os.path.exists(ov_path) else {}
    result = ["\t".join(rows[0])]
    for text, h, sid in rows[1:]:
        if sid in overrides:
            text = overrides[sid]
            done += 1
        elif text in en_to_ro and not SKIP_ID.match(sid):
            text = en_to_ro[text]
            done += 1
        result.append("\t".join([text, h, sid]))
    with open(OUT_TXT, "w", encoding="utf-16-le", newline="") as f:
        f.write("\r\n".join(result) + "\r\n")
    print(f"translated rows {done} / {len(rows) - 1} -> {os.path.abspath(OUT_TXT)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("prepare").add_argument("--force", action="store_true")
    v = sub.add_parser("validate")
    v.add_argument("batch", nargs="*", type=int)
    v.add_argument("-v", "--verbose", action="store_true")
    sub.add_parser("merge")
    a = ap.parse_args()
    sys.exit({"prepare": cmd_prepare, "validate": cmd_validate, "merge": cmd_merge}[a.cmd](a) or 0)
