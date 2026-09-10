# 可执行计划 v2：基于 WorkBuddy + dws + Obsidian 的智能多名片归档系统

> 定稿状态：可执行。WorkBuddy 支持多步+定时；收图用 `dws chat-messages --download-resources`
> 落本地 `images/* + 批次级 ledger.json`；模型先用 WorkBuddy 自带 VLM；Vault 新建；
> 目标双端可看 + `华东地区电脑销售` 级模糊+精细可检。钉钉只做采集+薄展示，真源在 Obsidian。

---

## 1. 架构与数据流

```
[钉钉 App 发图(+可选"2026深圳储能展")]
  -> [WorkBuddy 定时/手动 job: 归档]
  -> Step0 dws chat-messages --download-resources --out originals/<batch_id>/
       得 images/* + ledger.json
  -> adapter 解析 ledger -> job.json {msg_id, img_path, caption, time, sender}
  -> 去重 processed_msg_ids.sqlite
  -> StepA card_segmenter 切图 -> slices/
  -> StepB VLM 并发结构化 + 归一化(region/industry/role_type/aliases) + Pydantic 校验
  -> StepC dedup_resolver 判重写库
  -> 双写: Obsidian .md+webp(真源) + 钉钉 AI表追加行(薄索引)
  -> 冲突 -> 互动卡片(同人/新人) -> SUSPENDED 落盘 -> [WorkBuddy job: 回调] 履约
```

* 离线策略：存储转发。上线跑一次全补；全量重下靠 `msg_id` 幂等。
* 长挂起不驻内存：SUSPENDED 进 sqlite，TTL 7d，超时自动建新人+备注。

## 2. 装机清单

* 笔记本：WorkBuddy（含钉钉连接器，已登录）+ `dws`（PATH+鉴权）
  + Python 3.10+ `opencv-python numpy pydantic pyyaml rapidfuzz`
  + Obsidian 桌面 + Vault `D:\Obsidian\Cards\`（本仓库 `vault/` 为模板）。
* 手机：钉钉（发图、看表、点卡片）。
* 钉钉侧：1 张 AI表 + 1 个互动卡片模板（见 §6）。

## 3. 交付物（4 类）

```
visualCard/
  plan.md                  # 本文件
  requirements.txt
  run_batch.py             # 本地编排器(对应 WorkBuddy 归档 job，可手动/定时跑)
  skills/dws-fetch/SKILL.md + adapter.py
  skills/card-segmenter/SKILL.md + card_segmenter.py
  skills/obsidian-dedup-writer/SKILL.md + dedup_resolver.py + enrich.py + schemas.py
  vault/contacts/ attachments/ originals/ Contacts_Gallery.base  # Vault 模板
  tests/test_pipeline.py
```

## 4. Obsidian Schema（支持模糊+精细检索的关键）

* 文件名只用 uid：`contacts/card_<yyyymmdd>_<uuid8>.md`。
* 必写 frontmatter：`uid,name,aliases[],company,role,role_type,phones[],emails[],`
  `region,industry,product_keywords[],tags[],meet_event,meet_date,image_path,`
  `career_history[],source_msg_id`。
* 归一化词表（`enrich.py`）：杭州/上海/江苏→华东；渠道经理/客户经理→销售；
  笔记本/工作站→电脑。`phones/emails` 去 `-空格/+86`、小写。
* 判重：① phones/emails 命中→同一人（旧 company/role 进 career_history）；
  ② 无同名→新建；③ 同名无键可比/键冲突→SUSPENDED 发卡片。

## 5. WorkBuddy 任务（2 个）

* `归档 job`（手动按钮 + 定时）：跑 `run_batch.py --batch <batch_id>`。
* `回调 job`：收按钮 `same_person/new_person` → 读快照 → 合并/新建 → 回钉钉通知。
* VLM 先用自带，Prompt 约束 JSON + Pydantic 重试 2 次，并发 3。

## 6. 钉钉薄索引表（手机看）

字段：`姓名|公司|职位|电话|地区|行业|场景|原图链接|uid`，只增不改。

## 7. 检索

* 模糊：Omnisearch（拼音/typo/简称）。
* 精细：`.base` 过滤 `region=华东 AND role_type=销售 AND industry=电脑`。
* 验收样例：`华东地区电脑销售` 召回杭州笔记本渠道经理；`极星` 召回 `极星智算`。

## 8. Milestones

| ID | 验收 |
| --- | --- |
| M0 通路 | 1 批 dws→本地→1 条 .md→Bases 可见 |
| M1 切图 | 3-5 张倾斜实拍可用率>90%，竖版不变形 |
| M2 结构化 | 电话/邮箱零串行，三归一化字段>90% |
| M3 挂起 | 同名无键必弹卡片，两按钮均正确履约 |
| M4 双端 | 手机表可查，Bases 近100张<1s |
| M5 模糊查 | §7 样例通过 |

## 9. 本地一次性验证（本机无 dws/WorkBuddy 时）

```
pip install -r requirements.txt
python run_batch.py --demo   # 用合成名片图+模拟 ledger，走完全链，写 vault/ + 去重表
python -m pytest tests/ -q
```

`--demo` 不依赖 dws/WorkBuddy/Obsidian，只验 skills+脚本+schema；真机上把
`originals/<batch_id>/` 换成 dws 真实输出即可。
