"""Put the Romanian LanguageStrings into a COPY of the test project.

python scripts/ro_import.py [--src Liga1Orange.test.fbproject] [--dst Liga1Orange.ro.test.fbproject]

1. copies --src to --dst (the source project is never touched; *.test.fbproject is git-ignored)
2. exports data/loc/eng_us.db + -meta.xml from the copy (they hold the 7 imported teams)
3. DbCli import-table LanguageStrings db/LanguageStrings.ro.txt
4. injects the new .db AND the -meta.xml (AGENTS.md rule 5)
5. language-select flag: the English slot is `data/ui/artAssets/languageSelectFlags/ls14.big` (UK flag, ls18 = French).
   Its 12 frames (512x512 DXT5, 1 mip, 262272 bytes each, after a 10624-byte header) are replaced with the hand-made
   Romanian frames `assets/language_flags/france/{2,5,8,...,35}.DDS` (frame i = file 2+3i, checked against the French
   original by alpha). The label comes from db/translation_ro/overrides.json (`LanguageSelect_eng` = "Română").
Build db/LanguageStrings.ro.txt first: python scripts/ro_translate.py merge
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import re

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, '.env'))


def frosty(*args):
    exe = os.environ['FROSTYCLI_PATH']
    subprocess.run([exe, 'FIFA17', *args], cwd=os.path.dirname(exe), check=True)


FLAG_LEGACY = 'data/ui/artAssets/languageSelectFlags/ls14.big'
FLAG_DIR = os.path.join('assets', 'language_flags', 'france')
FRAME, HEADER = 262272, 10624


def build_flag(src_big, out_big):
    data = bytearray(open(src_big, 'rb').read())
    offs = [m.start() for m in re.finditer(rb'DDS \|\x00\x00\x00', bytes(data))]
    assert len(offs) == 12 and offs[0] == HEADER, offs
    for i, off in enumerate(offs):
        frame = open(os.path.join(ROOT, FLAG_DIR, f'{2 + 3 * i}.DDS'), 'rb').read()
        assert len(frame) == FRAME and frame[84:88] == b'DXT5', i
        data[off:off + FRAME] = frame
    open(out_big, 'wb').write(bytes(data))


def apply(project, keep_dir=None):
    """Romanian UI inside `project` (absolute path), in place: eng_us.db built from db/LanguageStrings.ro.txt (merged
    first, so the team names of the TSVs are in it) + meta XML, and the language-select flag."""
    import ro_translate
    ro_translate.cmd_merge(None)
    ro = os.path.join(ROOT, 'db', 'LanguageStrings.ro.txt')
    with tempfile.TemporaryDirectory() as tmp:
        db, xml = os.path.join(tmp, 'eng_us.DB'), os.path.join(tmp, 'eng_us-meta.XML')
        out = os.path.join(tmp, 'out', 'eng_us.DB')
        os.makedirs(os.path.dirname(out))
        frosty('export-legacy', project, 'data/loc/eng_us.db', db)
        frosty('export-legacy', project, 'data/loc/eng_us-meta.xml', xml)
        if not (os.path.exists(db) and os.path.exists(xml)):
            sys.exit('export-legacy failed')
        # DbCli writes a regenerated meta XML next to the output when the schema changed: start from the original
        out_xml = os.path.join(os.path.dirname(out), 'eng_us-meta.XML')
        shutil.copy2(xml, out_xml)
        subprocess.run([os.environ['DBCLI_PATH'], 'import-table', db, xml, 'LanguageStrings', ro, out], check=True)
        frosty('import-legacy', project, 'data/loc/eng_us.db', out)
        frosty('import-legacy', project, 'data/loc/eng_us-meta.xml', out_xml)
        big, new_big = os.path.join(tmp, 'ls14.big'), os.path.join(tmp, 'ls14_ro.big')
        frosty('export-legacy', project, FLAG_LEGACY, big)
        build_flag(big, new_big)
        frosty('import-legacy', project, FLAG_LEGACY, new_big)
        keep = keep_dir or os.path.join(ROOT, 'db', 'translation_ro', 'built')
        os.makedirs(keep, exist_ok=True)
        shutil.copy2(out, os.path.join(keep, 'eng_us.DB'))
        shutil.copy2(out_xml, os.path.join(keep, 'eng_us-meta.XML'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=os.path.join(ROOT, 'Liga1Orange.test.fbproject'))
    ap.add_argument('--dst', default=os.path.join(ROOT, 'Liga1Orange.ro.test.fbproject'))
    a = ap.parse_args()
    shutil.copy2(a.src, a.dst)
    print(f'copied {os.path.basename(a.src)} -> {os.path.basename(a.dst)}')
    apply(os.path.abspath(a.dst))
    print('done. Test in game:', a.dst)


if __name__ == '__main__':
    main()
