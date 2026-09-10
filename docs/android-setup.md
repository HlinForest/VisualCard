# 安卓端极简归档：装机清单与操作说明（钉盘为主版）

链路：手机拍照 → Obsidian 内选图上传 → AI Image OCR 插件调公司 LLM 解析 →
写本地库 → 分享归档钉盘（主存储）→ 自然语言检索 + deck 查看。
公司电脑不参与；零服务器；持续费用 ¥0。

## 一、装机清单

| # | 东西 | 哪装 | 费用 | 备注 |
|---|------|------|------|------|
| 1 | Obsidian Mobile | 安卓应用市场 / Google Play | 免费 | 已装，待建库 |
| 2 | BRAT 插件 | Obsidian 社区插件市场 | 免费 | 装 OCR 插件的跳板（插件已上架社区市场则跳过） |
| 3 | AI Image OCR（`rootiest/obsidian-ai-image-ocr`） | 经 BRAT 装，MIT | 免费 | 核心：选图→解析→写库 |
| 4 | Omnisearch | 社区插件市场 | 免费 | 模糊检索兜底（拼音/错字/简称） |
| 5 | 公司 LLM API key | 找公司 IT 申请 | ¥0（公司） | 只填插件设置，不进仓库 |
| 6 | 钉钉 App（含 10GB 企业钉盘） | 已有 | ¥0 | 主存储：原图 + 解析结果归档 |

**不需要装**：Tasker、Python、dws、钉钉机器人、Obsidian Sync（以后要双端实时再加，库结构不用动）。

**不需要的持续费用**：Sync（没买）、云服务器（没有）、外部 API（走公司）。

## 二、建库（三步，全在手机上）

1. 新建本地库 `Cards`，记下本机路径；内建 `contacts/ attachments/ inbox/`。
2. 把本仓库 `vault/` 下 `Contacts_Gallery.base`、`Search_Deck.base`、`Review_Dedup.md`
   拷进库根（图墙 + 检索 deck + 判重自检）。
3. 插件配置照 `shortcuts/android-plugin.md` 走：Custom endpoint → 公司地址/模型/key；
   prompt 粘 `prompts/card_parse.md`；输出目录 `contacts/`，命名 `card_YYYYMMDD_*`。

## 三、日常用法

* **拍照归档**：相机拍（含多名片合影）→ Obsidian 里对照片跑插件提取 →
  出 `.md` 进 `contacts/` → 系统分享把 `.md` + 原图存进钉盘 `Cards/`（主归档，两下点完）。
* **钉钉转来的**：聊天图片长按保存到相册 → 同上。
* **每周一次**：库 zip 打包存钉盘 `Cards/_backup/`；打开 `Review_Dedup.md` 清一次待确认。
* **查**：自然语言问（见 §四）或图墙翻，或 Base 按地区/行业/职位过滤。

## 四、自然语言检索

1. 打开 `Search_Ask.md`，写下问题（如“谁是华东卖电脑的”）。
2. 把库索引（`Search_Index.json`，见 `shortcuts/android-plugin.md` 生成法）+ 问题
   发给公司 LLM（prompt 见 `prompts/card_search.md`，手机浏览器/AI 应用均可）。
3. 模型返回 uid 列表 → 填进 `Search_Deck.base` 的 uid 过滤 → deck 直接看人、点看原件。

## 五、验收

M0 单卡出库 → M1 三卡合影拆 3 条 → M2 电话邮箱无串行 →
M3 钉盘 `Cards/` 有归档 → M4 自然语言问出人 → M5 deck 可点看原件。
