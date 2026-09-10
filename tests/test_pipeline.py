"""端到端冒烟：adapter/切图/富化/判重/整批。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "dws-fetch"))
sys.path.insert(0, str(ROOT / "skills" / "card-segmenter"))
sys.path.insert(0, str(ROOT / "skills" / "obsidian-dedup-writer"))

from adapter import load_ledger  # noqa: E402
from card_segmenter import segment_cards  # noqa: E402
from dedup_resolver import resolve  # noqa: E402
from enrich import enrich, region_of, role_type_of, industry_of  # noqa: E402
from run_batch import run_batch  # noqa: E402


def test_enrich_supports_fuzzy_query():
    assert region_of("杭州") == "华东"
    assert role_type_of("渠道经理") == "销售"
    assert industry_of("笔记本") == "电脑"


def test_dedup_new_merge_suspend(tmp_path):
    vault = tmp_path / "v"
    c1 = enrich({"name": "张伟", "company": "A", "role": "工程师",
                 "phones": ["13800000001"], "emails": [], "city": "杭州", "product_hint": "笔记本"})
    assert resolve(c1, vault)[0] == "new"
    c2 = enrich({"name": "张伟", "company": "B", "role": "总监",
                 "phones": ["13800000001"], "emails": [], "city": "杭州", "product_hint": "笔记本"})
    st, _ = resolve(c2, vault)
    assert st == "merged"
    c3 = enrich({"name": "张伟", "company": "C", "role": "销售",
                 "phones": [], "emails": [], "city": "苏州", "product_hint": "工作站"})
    assert resolve(c3, vault)[0] == "suspended"


def test_full_demo_batch(tmp_path):
    import run_batch as rb
    batch = tmp_path / "b"
    (batch / "images").mkdir(parents=True)
    rb._synthetic_photo(batch / "images" / "p.jpg")
    (batch / "ledger.json").write_text(json.dumps(
        {"batch_id": "t", "messages": [
            {"msg_id": "m1", "sender": "s", "time": "2026-09-10",
             "text": "2026深圳储能展", "images": ["images/p.jpg"]}]}), encoding="utf-8")
    jobs = load_ledger(batch)
    assert len(jobs) == 1 and jobs[0]["caption"] == "2026深圳储能展"
    slices = segment_cards(jobs[0]["img_path"], batch / "slices", stem="p")
    assert len(slices) >= 1, "合成图应至少切出 1 张"
    stats = run_batch(batch, tmp_path / "v", tmp_path / "rows.json")
    assert stats["new"] + stats["merged"] >= 1
    assert (tmp_path / "v" / "contacts").glob("*.md")
