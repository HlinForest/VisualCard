# Skill: dws-fetch

## 用途
把 `dws chat-messages --download-resources --out originals/<batch_id>/` 的产物
（`images/* + 批次级 ledger.json`）解析为标准 job 列表，隔离 dws 格式变化。

## 输入（batch 目录）
```
originals/<batch_id>/
  images/img1.jpg ...
  ledger.json   # 批次级：{"batch_id","messages":[{"msg_id","sender","time","text","images":["images/img1.jpg"]}]}
```

## 输出
`job.json` 列表项：`{msg_id, sender, time, img_path(绝对), caption, batch_id}`。
`caption` 即同批文字（如“2026深圳储能展”），后续赋给 `meet_event`。

## 接口
`adapter.load_ledger(batch_dir) -> list[dict]`
