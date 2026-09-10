# Skill: card-segmenter

## 用途
本地多名片切片：输入 dws 落盘原图，输出透视拉平切片。失败不抛异常——
返回空列表，由调用方把原图直通 VLM，保证整批不卡死。

## 接口
`card_segmenter.segment_cards(img_path, out_dir, stem) -> list[str]`（绝对路径）

## 要点
相对面积（2%~60% 全图）+ `approxPolyDP` 四边形 + 凸包 + 横/竖长宽比
（横 1.4~2.0，竖 0.5~0.72）+ 包围盒 IoU-NMS；横版输出 1050x600，竖版 600x1050。
