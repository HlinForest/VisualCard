# Skill: obsidian-dedup-writer

## 用途
VLM 原始 JSON → 归一化富化 → 判重 → 写 Obsidian（真源）+ 钉钉薄索引行。
文件名只用 uid：`contacts/card_<yyyymmdd>_<uuid8>.md`。

## 接口
* `schemas.CardJSON`：VLM 输出强类型（Pydantic 校验）。
* `enrich.enrich(raw, meet_event, meet_date) -> dict`：电话邮箱归一化 + region/industry/role_type + aliases。
* `dedup_resolver.resolve(card, vault) -> ("new"|"merged"|"suspended", info)` 并落盘。

## 判重
phones/emails 命中→merged（旧 company/role 进 career_history）；
无同名→new；同名无键可比/键冲突→suspended（快照等回调）。
