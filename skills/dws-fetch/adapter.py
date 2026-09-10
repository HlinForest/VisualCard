"""ledger(JSON, 批次级) -> 标准 job 列表适配器。"""
import json
from pathlib import Path


def load_ledger(batch_dir: str | Path) -> list[dict]:
    batch = Path(batch_dir)
    ledger_p = batch / "ledger.json"
    if not ledger_p.exists():
        # 兼容：目录里只有图片、无 ledger，则每图一个 job，caption 为空
        jobs = []
        for p in sorted((batch / "images").glob("*")) if (batch / "images").exists() else sorted(batch.glob("*.jpg")):
            jobs.append({"msg_id": p.stem, "sender": "", "time": "",
                         "img_path": str(p.resolve()), "caption": "",
                         "batch_id": batch.name})
        return jobs
    data = json.loads(ledger_p.read_text(encoding="utf-8"))
    batch_id = data.get("batch_id", batch.name)
    jobs: list[dict] = []
    for m in data.get("messages", []):
        caption = (m.get("text") or "").strip()
        for rel in m.get("images", []):
            p = (batch / rel).resolve() if not Path(rel).is_absolute() else Path(rel)
            jobs.append({"msg_id": m.get("msg_id", p.stem), "sender": m.get("sender", ""),
                         "time": m.get("time", ""), "img_path": str(p),
                         "caption": caption, "batch_id": batch_id})
    return jobs
