#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""scan-diff - snapshot & diff for recon target lists.

Save a snapshot of your subdomain / URL / port list today, diff it against
the next scan tomorrow: what appeared, what disappeared. Pairs well with
httpx, subfinder, amass output - or your own batch scripts.

Zero third-party dependencies.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

__version__ = "0.1.0"


def clean_lines(lines):
    """Strip blanks/comments, dedupe, sort - so diffs never lie about order."""
    out, seen = [], set()
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("#"):
            continue
        if s in seen:
            continue
        seen.add(s)
        out.append(s)
    return sorted(out)


def snapshot_lines(lines, source=""):
    return {"schema": 1,
            "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "source": source, "targets": clean_lines(lines)}


def snapshot_file(path):
    p = Path(path)
    return snapshot_lines(p.read_text(encoding="utf-8", errors="replace").splitlines(), str(p))


def snapshot_stdin():
    return snapshot_lines(sys.stdin.read().splitlines(), "<stdin>")


def to_json(snap):
    return json.dumps(snap, ensure_ascii=False, indent=2)


def load_snapshot(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(d.get("targets"), list):
        raise SystemExit(f"not a scan-diff snapshot (no targets list): {path}")
    return d


def diff_snapshots(old, new):
    o, n = set(old["targets"]), set(new["targets"])
    return {"added": sorted(n - o), "removed": sorted(o - n), "same": sorted(o & n)}


def has_changes(d):
    return bool(d["added"] or d["removed"])


def render_diff(d, old_source="", new_source=""):
    lines = []
    for label, items in (("NEW", d["added"]), ("GONE", d["removed"])):
        lines.append(f"[{label}] {len(items)}")
        for t in items:
            lines.append(f"  {t}")
    lines.append(f"[same] {len(d['same'])}")
    if old_source or new_source:
        lines.append(f"({old_source or '?'} -> {new_source or '?'})")
    return "\n".join(lines)


EXAMPLES = """examples:
  scan-diff snapshot today.txt -o snap-1011.json
  cat subfinder.txt | scan-diff snapshot - -o snap-1012.json
  scan-diff diff snap-1011.json snap-1012.json --fail   # exit 2 if anything changed
"""


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="scan-diff", description=__doc__.strip().splitlines()[0],
        epilog=EXAMPLES, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_snap = sub.add_parser("snapshot", help="save a snapshot of a target list")
    p_snap.add_argument("targets", help="text file, one target per line; '-' = stdin")
    p_snap.add_argument("-o", "--out", required=True, help="snapshot .json to write")

    p_diff = sub.add_parser("diff", help="diff two snapshots")
    p_diff.add_argument("old", help="older snapshot .json")
    p_diff.add_argument("new", help="newer snapshot .json")
    p_diff.add_argument("--fail", action="store_true", help="exit code 2 if anything changed")

    ap.add_argument("-V", "--version", action="version", version=f"scan-diff {__version__}")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if args.cmd == "snapshot":
        snap = snapshot_stdin() if args.targets == "-" else snapshot_file(args.targets)
        Path(args.out).expanduser().write_text(to_json(snap), encoding="utf-8")
        print(f"snapshot saved: {len(snap['targets'])} targets -> {args.out}", file=sys.stderr)
        return 0

    d = diff_snapshots(load_snapshot(args.old), load_snapshot(args.new))
    print(render_diff(d, args.old, args.new))
    return 2 if (args.fail and has_changes(d)) else 0


if __name__ == "__main__":
    sys.exit(main())
