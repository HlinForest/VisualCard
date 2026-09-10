# 安卓插件配置步骤（照点操作，约 15 分钟）

目标：Obsidian 里选图 → 公司 LLM 解析 → `contacts/` 出库 → 分享归档钉盘。

## 0. 前置

- Obsidian Mobile 已建本地库 `Cards`（`contacts/ attachments/ inbox/`），
  本仓库 `vault/` 下 3 个文件已拷入（见 §5）。
- 公司 LLM 的 endpoint URL、model ID、key 在手（OpenAI 兼容 chat completions）。

## 1. 装插件

1. 设置 → 第三方插件 → 关闭安全模式 → 浏览 → 先装 **BRAT** 并启用。
2. 命令面板 → `BRAT: Add beta plugin` → 填
   `https://github.com/rootiest/obsidian-ai-image-ocr` → Add plugin → 启用。
   （它已上架社区市场时可直接搜 `AI Image OCR` 安装，跳过 BRAT。）
3. 同市场装 **Omnisearch** 并启用。

## 2. 配 Provider（连公司 API）

插件设置 → Provider 选 **Custom（OpenAI-compatible）**：

- Endpoint：公司地址全文（如 `https://xxx/v1/chat/completions`），照 IT 给的抄。
- Model：照 IT 给的填。
- API Key：粘 key。**只存手机插件设置，不进仓库、不同步出本机。**
- 点测试：选一张名片跑一次，能出文字即通；401/404 先核对地址和 key。

## 3. 配 prompt 与输出

- Custom prompt：全文粘本仓库 `prompts/card_parse.md`。
- 输出目标：**Create new note**，目录 `contacts/`，
  文件名模板 `card_{{date:YYYYMMDD}}_` + 随机（插件无 uuid 占位时手动补 4 位）。
- Header 模板嵌入原图（`{{image.image}}`），保证 deck 的“名片原件”列有图。
- 批量：命令 `Extract text from image folder` 对准 `inbox/`。

## 4. 归档到钉盘（主存储，两步）

1. 解析出的 `.md` + `attachments/` 原图 → 系统分享 → 钉钉 → 存入钉盘 `Cards/` 当天文件夹。
2. 每周：库 zip → 钉盘 `Cards/_backup/`；打开 `Review_Dedup.md` 清待确认。

## 5. 本仓库拷入手机的 3 个文件

- `vault/Contacts_Gallery.base` → 库根（常驻图墙）。
- `vault/Search_Deck.base` → 库根（检索结果 deck，查时填 uid 列表）。
- `vault/Review_Dedup.md` → 库根（每周判重自检）。

## 6. 自然语言检索操作

1. 生成索引：在库里跑一次全文搜集 contacts frontmatter，拼成
   `Search_Index.json`（`uid|姓名|公司|职位|电话|地区|行业|场景` 每行一人；
   上千人时先按地区/行业粗筛 50 以内）。
2. 手机浏览器/AI 应用开一会话：system 粘 `prompts/card_search.md`，
   user 发“问题 + 索引全文”。
3. 返回的 uid 填进 `Search_Deck.base` 过滤 → deck 看人、点看原件。
