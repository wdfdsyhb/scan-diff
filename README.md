# scan-diff · 侦察清单快照对比

[![CI](https://github.com/wdfdsyhb/scan-diff/actions/workflows/tests.yml/badge.svg)](https://github.com/wdfdsyhb/scan-diff/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)

> 把侦察输出存成带时间戳的 JSON 快照，一条命令 diff 出新增/消失的资产——不用再肉眼对清单。
>
> English: Save each recon list as a timestamped JSON snapshot, then diff scans in one command — new and dropped assets surface themselves.

## Why

批量侦察的产出（subfinder / httpx / 端口扫描）每次都在变，但"这次比上次多了什么"要靠肉眼对。scan-diff 把清单变成带时间戳的快照，diff 只报变化——配合 cron 或每次挖洞前跑一遍，新资产主动送上门。

## Usage

```bash
scan-diff snapshot today.txt -o snap-1011.json        # 存快照
cat subfinder.txt | scan-diff snapshot - -o snap-1012.json
scan-diff diff snap-1011.json snap-1012.json          # 对比
scan-diff diff old.json new.json --fail               # 有变化时退出码 2（接脚本）
```

输出：

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

- 清单读入时自动去空行/去注释/去重/排序——diff 永远不会因为顺序和重复撒谎
- 快照是纯 JSON（schema/created/source/targets），肉眼可读，git 可管
- 零依赖，单文件

## Pairing

配合 [fake200](https://github.com/wdfdsyhb/fake200)（过滤 WAF 假 200）使用：新子域进来了，先验真再挖。

## License

MIT

---

## English

Full English documentation: [README_EN.md](README_EN.md)
