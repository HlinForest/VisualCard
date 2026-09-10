# VisualCard · 智能多名片归档系统

手机钉钉拍照采集 → `dws` 落盘原图 → 本地 OpenCV 切片 → VLM 结构化 →
判重写库 → Obsidian 本地沉淀（真源）+ 钉钉 AI 表（手机薄索引）。
支持 `华东地区电脑销售` 级模糊 + 精细联合检索。

```
[钉钉 App 发图(+可选"2026深圳储能展")]
  -> [WorkBuddy 定时/手动 job: 归档]
  -> Step0 dws chat-messages --download-resources --out originals/<batch_id>/
  -> adapter 解析 ledger -> job.json
  -> 去重 processed_msg_ids.sqlite（幂等，全量重下不重写）
  -> StepA card_segmenter 切图 -> slices/
  -> StepB VLM 并发结构化 + 归一化(region/industry/role_type) + Pydantic 校验
  -> StepC dedup_resolver 判重写库
  -> 双写: Obsidian .md+webp(真源) + 钉钉 AI表追加行(薄索引)
  -> 同名无键冲突 -> 互动卡片(同人/新人) -> SUSPENDED 落盘 -> 回调 job 履约
```

## 目录结构

```
plan.md                  # 可执行计划 v2（定稿）
requirements.txt
run_batch.py             # 本地编排器 = WorkBuddy 归档 job 的可执行版
skills/dws-fetch/        # ledger(JSON,批次级) -> 标准 job 列表适配器
skills/card-segmenter/   # 多名片 OpenCV 切片
skills/obsidian-dedup-writer/  # 归一化富化 + 判重写库
vault/                   # Vault 模板: contacts/ attachments/ originals/ Contacts_Gallery.base
tests/                   # 冒烟测试
```

## 5 分钟自检（无需 dws / VLM / Obsidian）

```powershell
pip install -r requirements.txt
python run_batch.py --demo   # 合成图+模拟ledger+VLM mock，全链跑通，应输出 new:2
python -m pytest tests/ -q   # 3 passed
```

## 真机部署

1. **Python**：`pip install -r requirements.txt`，`--demo` 自检通过。
2. **dws**：确认 PATH + 已登录，输出到 `vault/originals/<batch_id>/`（`images/* + ledger.json`），
   用 `adapter.load_ledger` 确认能解析出 `caption`（关联 `meet_event`）。
3. **Obsidian**：新建库，把 `vault/` 下四个目录拷过去；装 `Omnisearch`；用
   `Contacts_Gallery.base` 开图墙，加过滤 `region=华东 AND role_type=销售 AND industry=电脑`。
4. **钉钉侧**：AI 表建 9 列（`vault/dingtalk_rows.json` 即行样例）；
   互动卡片两个按钮 `same_person` / `new_person`。
5. **WorkBuddy 两任务**：归档 job（`run_batch.py --batch ...`）+ 回调 job（读 `_suspended` 快照履约）。
   真实 VLM 只需替换 `_mock_vlm` 一个函数。

## 关键设计

* 文件名只用 uid（`card_<date>_<uuid8>.md`），跳槽不改名；`region/industry/role_type`
  三归一化字段是模糊检索（杭州→华东、渠道经理→销售、笔记本→电脑）的关键。
* 判重三分支：phones/emails 命中→merged（旧公司进 `career_history`）；无同名→new；
  同名无键可比→suspended 发卡片，TTL 7d。
* 切片失败不卡批：返回空则原图直通 VLM；`cv2` 读写走 `imdecode/imencode`，兼容 Windows 非 ASCII 路径。

## Milestones

M0 通路 → M1 切图可用率>90% → M2 电话邮箱零串行 → M3 挂起必弹卡片 →
M4 双端可查 → M5 `华东地区电脑销售`样例通过。详见 `plan.md`。
