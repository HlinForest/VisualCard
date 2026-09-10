"""本地编排器 = WorkBuddy 归档 job 的可执行版本。
真实: python run_batch.py --batch vault/originals/<batch_id>
演示: python run_batch.py --demo（合成图+模拟ledger+VLM mock，全链跑通）
"""
import argparse
import json
import sqlite3
import sys
from datetime import date
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "skills" / "dws-fetch"))
sys.path.insert(0, str(ROOT / "skills" / "card-segmenter"))
sys.path.insert(0, str(ROOT / "skills" / "obsidian-dedup-writer"))

from adapter import load_ledger  # noqa: E402
from card_segmenter import segment_cards, write_image  # noqa: E402
from dedup_resolver import resolve  # noqa: E402
from enrich import enrich  # noqa: E402
from schemas import CardJSON  # noqa: E402

MOCK_VLM = [
    {"name": "张伟", "company": "极星智算", "role": "渠道经理",
     "phones": ["138-0000-0001"], "emails": ["ZhangWei@polaris.ai"],
     "city": "杭州", "product_hint": "笔记本"},
    {"name": "李娜", "company": "申城电子", "role": "大客户销售",
     "phones": ["13900000002"], "emails": ["lina@example.com"],
     "city": "苏州", "product_hint": "工作站"},
]


def _mock_vlm(_img: str, i: int) -> dict:
    return dict(MOCK_VLM[i % len(MOCK_VLM)])


def _synthetic_photo(path: Path) -> None:
    """白底纸上两张深色名片框，保证 Canny+四边形可检出。"""
    img = np.full((900, 1200, 3), 240, dtype=np.uint8)
    cv2.rectangle(img, (80, 120), (80 + 500, 120 + 300), (30, 30, 30), 4)
    cv2.rectangle(img, (620, 420), (620 + 500, 420 + 300), (30, 30, 30), 4)
    cv2.putText(img, "Zhang Wei", (120, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (30, 30, 30), 2)
    cv2.putText(img, "Li Na", (660, 550), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (30, 30, 30), 2)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_image(path, img, ".jpg")


def _mark_processed(db: Path, msg_id: str) -> bool:
    db.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE IF NOT EXISTS done(msg TEXT PRIMARY KEY)")
    row = con.execute("SELECT 1 FROM done WHERE msg=?", (msg_id,)).fetchone()
    if row:
        con.close()
        return False
    con.execute("INSERT INTO done VALUES(?)", (msg_id,))
    con.commit()
    con.close()
    return True


def run_batch(batch_dir: Path, vault: Path, out_rows: Path) -> dict:
    jobs = load_ledger(batch_dir)
    stats = {"jobs": len(jobs), "new": 0, "merged": 0, "suspended": 0, "skipped": 0, "rows": []}
    idx = 0
    for job in jobs:
        if not _mark_processed(vault / "processed_msg_ids.sqlite", job["msg_id"]):
            stats["skipped"] += 1
            continue
        slices = segment_cards(job["img_path"], batch_dir / "slices", stem=Path(job["img_path"]).stem)
        if not slices:  # 兜底：切不出则原图直通 VLM
            slices = [job["img_path"]]
        for s in slices:
            raw = CardJSON(**_mock_vlm(s, idx)).model_dump()
            idx += 1
            card = enrich(raw, meet_event=job["caption"] or "演示批次",
                          meet_date=job.get("time") or date.today().isoformat())
            status, info = resolve(card, vault, slice_path=s if Path(s).exists() else "",
                                   source_msg_id=job["msg_id"])
            stats[status if status in stats else "suspended"] = stats.get(status, 0) + 1
            stats["rows"].append({"姓名": card["name"], "公司": card["company"],
                                  "职位": card["role"], "电话": (card["phones"] + [""])[0],
                                  "地区": card["region"], "行业": card["industry"],
                                  "场景": card["meet_event"], "uid": info.get("file", ""),
                                  "状态": status})
    out_rows.write_text(json.dumps(stats["rows"], ensure_ascii=False, indent=2), encoding="utf-8")
    return stats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="")
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    vault = ROOT / "vault"
    if args.demo:
        batch = ROOT / "vault" / "originals" / "demo_batch"
        (batch / "images").mkdir(parents=True, exist_ok=True)
        photo = batch / "images" / "photo1.jpg"
        _synthetic_photo(photo)
        (batch / "ledger.json").write_text(json.dumps(
            {"batch_id": "demo_batch", "messages": [
                {"msg_id": "m1", "sender": "me", "time": date.today().isoformat(),
                 "text": "2026深圳储能展", "images": ["images/photo1.jpg"]}]},
            ensure_ascii=False), encoding="utf-8")
        batch_dir = batch
    else:
        if not args.batch:
            ap.error("--batch <originals/xxx> 或 --demo 二选一")
        batch_dir = Path(args.batch)
    stats = run_batch(batch_dir, vault, vault / "dingtalk_rows.json")
    print(json.dumps({k: v for k, v in stats.items() if k != "rows"}, ensure_ascii=False))
    print(f"rows -> {vault / 'dingtalk_rows.json'}")


if __name__ == "__main__":
    main()
