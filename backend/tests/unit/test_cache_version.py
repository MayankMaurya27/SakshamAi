"""Unit tests for version-based cache purge."""

from pathlib import Path

from services.cache_version import purge_cache_dir_if_version_changed, purge_caches_on_version_change


def test_purge_cache_dir_if_version_changed_removes_json_on_version_bump(tmp_path: Path):
    cache_dir = tmp_path / "summary_cache"
    cache_dir.mkdir()
    (cache_dir / "abc123.json").write_text('{"summary": "old"}', encoding="utf-8")
    (cache_dir / ".cache_version").write_text("v1", encoding="utf-8")

    removed = purge_cache_dir_if_version_changed(cache_dir, "v2", "summary")

    assert removed == 1
    assert not (cache_dir / "abc123.json").exists()
    assert (cache_dir / ".cache_version").read_text(encoding="utf-8") == "v2"


def test_purge_cache_dir_if_version_changed_skips_when_version_matches(tmp_path: Path):
    cache_dir = tmp_path / "summary_cache"
    cache_dir.mkdir()
    (cache_dir / "abc123.json").write_text('{"summary": "keep"}', encoding="utf-8")
    (cache_dir / ".cache_version").write_text("v1", encoding="utf-8")

    removed = purge_cache_dir_if_version_changed(cache_dir, "v1", "summary")

    assert removed == 0
    assert (cache_dir / "abc123.json").exists()


def test_purge_cache_dir_if_version_changed_initializes_marker_without_purge(tmp_path: Path):
    cache_dir = tmp_path / "quiz_cache"
    cache_dir.mkdir()
    (cache_dir / "quiz1.json").write_text('{"questions": []}', encoding="utf-8")

    removed = purge_cache_dir_if_version_changed(cache_dir, "v1|v2", "quiz")

    assert removed == 0
    assert (cache_dir / "quiz1.json").exists()
    assert (cache_dir / ".cache_version").read_text(encoding="utf-8") == "v1|v2"


def test_purge_caches_on_version_change_for_both_dirs(tmp_path: Path, monkeypatch):
    from config.settings import Settings

    settings = Settings(
        data_dir=tmp_path,
        summary_cache_dir=tmp_path / "summary_cache",
        quiz_cache_dir=tmp_path / "quiz_cache",
        localize_cache_dir=tmp_path / "localize_cache",
        summary_cache_version="summary-v2",
        quiz_cache_version="quiz-v2",
        saksham_index_version="index-v2",
        localize_cache_version="localize-v2",
    )
    settings.summary_cache_dir.mkdir(parents=True)
    settings.quiz_cache_dir.mkdir(parents=True)
    settings.localize_cache_dir.mkdir(parents=True)
    (settings.summary_cache_dir / "old.json").write_text("{}", encoding="utf-8")
    (settings.quiz_cache_dir / "old.json").write_text("{}", encoding="utf-8")
    (settings.localize_cache_dir / "old.json").write_text("{}", encoding="utf-8")
    (settings.summary_cache_dir / ".cache_version").write_text("summary-v1", encoding="utf-8")
    (settings.quiz_cache_dir / ".cache_version").write_text("quiz-v1|index-v1", encoding="utf-8")
    (settings.localize_cache_dir / ".cache_version").write_text("localize-v1", encoding="utf-8")

    result = purge_caches_on_version_change(settings)

    assert result == {"summary_removed": 1, "quiz_removed": 1, "localize_removed": 1}
    assert not (settings.summary_cache_dir / "old.json").exists()
    assert not (settings.quiz_cache_dir / "old.json").exists()
    assert not (settings.localize_cache_dir / "old.json").exists()
