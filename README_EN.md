# scan-diff

[![CI](https://github.com/wdfdsyhb/scan-diff/actions/workflows/tests.yml/badge.svg)](https://github.com/wdfdsyhb/scan-diff/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

> Save each recon list as a timestamped JSON snapshot, then diff scans in one command — new and dropped assets surface themselves.
>
> 🇨🇳 中文文档: [README.md](README.md)

## Why

Recon output (subfinder / httpx / port scans) changes every run, but "what did this scan add since the last one" usually means eyeballing lists. scan-diff turns lists into timestamped snapshots and the diff reports only the changes — run it from cron or before every bug-hunt session, and new assets come to you.

## Usage

```bash
scan-diff snapshot today.txt -o snap-1011.json        # save a snapshot
cat subfinder.txt | scan-diff snapshot - -o snap-1012.json
scan-diff diff snap-1011.json snap-1012.json          # compare
scan-diff diff old.json new.json --fail               # exit code 2 on changes (for scripts)
```

Output:

```
[NEW] 2
  new.example.com
  staging.example.com
[GONE] 1
  old.example.com
[same] 154
(snap-1011.json -> snap-1012.json)
```

## Design

- Lists are normalized on read: blank lines, comments, duplicates removed, sorted — the diff never lies because of ordering or duplicates
- Snapshots are plain JSON (schema/created/source/targets), human-readable and git-friendly
- Zero dependencies, single file

## Pairing

Works well with [fake200](https://github.com/wdfdsyhb/fake200) (filters WAF fake 200s): when a new subdomain shows up, verify it before you dig in.

## License

MIT
