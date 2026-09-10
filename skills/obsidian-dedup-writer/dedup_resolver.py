"""判重 + 写库。new/merged/suspended 三分支。"""
import shutil
import uuid
from datetime import date
from pathlib import Path

import yaml

from enrich import same_name


def _read_frontmatter(md: Path) -> dict:
    txt = md.read_text(encoding="utf-8")
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        if end != -1:
            return yaml.safe_load(txt[3:end]) or {}
    return {}


def _write_md(md: Path, fm: dict, body: str = "") -> None:
    md.write_text("---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n" + body,
                  encoding="utf-8")


def _index(vault: Path) -> list[tuple[Path, dict]]:
    out = []
    for md in sorted((vault / "contacts").glob("*.md")):
        try:
            out.append((md, _read_frontmatter(md)))
        except Exception:
            continue
    return out


def resolve(card: dict, vault: str | Path, slice_path: str = "",
            source_msg_id: str = "") -> tuple[str, dict]:
    vault = Path(vault)
    (vault / "contacts").mkdir(parents=True, exist_ok=True)
    (vault / "attachments").mkdir(parents=True, exist_ok=True)
    keys_new = set(card.get("phones", [])) | set(card.get("emails", []))

    for md, fm in _index(vault):
        keys_old = set(fm.get("phones", [])) | set(fm.get("emails", []))
        if keys_new and keys_new & keys_old:
            hist = fm.get("career_history", [])
            if fm.get("company") and fm["company"] != card.get("company"):
                hist.append({"company": fm.get("company"), "role": fm.get("role", ""),
                             "period": f"~{date.today().isoformat()}"})
            fm.update({k: card.get(k, fm.get(k)) for k in
                       ("name", "company", "role", "role_type", "phones", "emails",
                        "region", "industry", "product_keywords", "meet_event", "meet_date")})
            fm["career_history"] = hist
            if slice_path:
                dest = vault / "attachments" / f"{fm['uid']}.webp"
                shutil.copyfile(slice_path, dest)
                fm["image_path"] = f"attachments/{dest.name}"
            _write_md(md, fm)
            return "merged", {"file": str(md)}

    for md, fm in _index(vault):
        if same_name(fm.get("name", ""), card.get("name", "")):
            if not keys_new or not (keys_new & set(fm.get("phones", [])) | set(fm.get("emails", []))):
                snap_dir = vault / "originals" / "_suspended"
                snap_dir.mkdir(parents=True, exist_ok=True)
                return "suspended", {"conflict_with": str(md), "card": card,
                                     "source_msg_id": source_msg_id}

    uid = f"card_{date.today().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}"
    img_rel = ""
    if slice_path:
        dest = vault / "attachments" / f"{uid}.webp"
        shutil.copyfile(slice_path, dest)
        img_rel = f"attachments/{dest.name}"
    fm = {"uid": uid, **card, "image_path": img_rel, "source_msg_id": source_msg_id}
    md = vault / "contacts" / f"{uid}.md"
    _write_md(md, fm)
    return "new", {"file": str(md)}
