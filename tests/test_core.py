import scan_diff as sd


def test_clean_lines_dedups_sorts_ignores_comments():
    raw = ["# comment", "b.com", "a.com", "b.com", "", "  "]
    assert sd.clean_lines(raw) == ["a.com", "b.com"]


def test_snapshot_has_schema_and_timestamp(tmp_path):
    f = tmp_path / "hosts.txt"
    f.write_text("a.com\nb.com\n", encoding="utf-8")
    snap = sd.snapshot_file(f)
    assert snap["schema"] == 1
    assert snap["targets"] == ["a.com", "b.com"]
    assert "created" in snap and "source" in snap


def test_snapshot_json_roundtrip(tmp_path):
    f = tmp_path / "hosts.txt"
    f.write_text("a.com\n", encoding="utf-8")
    out = tmp_path / "s.json"
    snap = sd.snapshot_file(f)
    out.write_text(sd.to_json(snap), encoding="utf-8")
    assert sd.load_snapshot(out)["targets"] == ["a.com"]


def test_diff_added_removed_same():
    old = {"targets": ["a.com", "b.com"]}
    new = {"targets": ["b.com", "c.com"]}
    d = sd.diff_snapshots(old, new)
    assert d["added"] == ["c.com"]
    assert d["removed"] == ["a.com"]
    assert d["same"] == ["b.com"]


def test_has_changes():
    assert sd.has_changes({"added": ["x"], "removed": [], "same": []})
    assert not sd.has_changes({"added": [], "removed": [], "same": ["x"]})
