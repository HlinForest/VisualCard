"""多名片 OpenCV 切片：相对面积 + 四边形校验 + 横竖自适应 + NMS。"""
import cv2
import numpy as np
from pathlib import Path


def read_image(path: str | Path):
    """cv2.imread 在 Windows 非 ASCII 路径下返回 None，改用 fromfile+imdecode。"""
    data = np.fromfile(str(path), dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR)


def write_image(path: str | Path, img: np.ndarray, ext: str = ".webp", quality: int = 90) -> bool:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    params = [cv2.IMWRITE_WEBP_QUALITY, quality] if ext == ".webp" else []
    ok, buf = cv2.imencode(ext, img, params)
    if not ok:
        return False
    buf.tofile(str(path))
    return True


def _order(pts: np.ndarray) -> np.ndarray:
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)],
                     pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)


def _iou(a, b) -> float:
    xa, ya, wa, ha = a
    xb, yb, wb, hb = b
    xi = max(0, min(xa + wa, xb + wb) - max(xa, xb))
    yi = max(0, min(ya + ha, yb + hb) - max(ya, yb))
    inter = xi * yi
    union = wa * ha + wb * hb - inter
    return inter / union if union else 0.0


def segment_cards(img_path: str | Path, out_dir: str | Path, stem: str = "slice") -> list[str]:
    img_path, out_dir = Path(img_path), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    img = read_image(img_path)
    if img is None:
        return []
    H, W = img.shape[:2]
    total = H * W
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    med = float(np.median(gray))
    lo, hi = int(max(0, 0.66 * med)), int(min(255, 1.33 * med))
    edges = cv2.Canny(gray, lo, hi)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=1)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cands: list[tuple[np.ndarray, tuple]] = []
    for c in contours:
        area = cv2.contourArea(c)
        if not (0.02 * total < area < 0.60 * total):
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        box = cv2.boundingRect(c)
        if len(approx) == 4 and cv2.isContourConvex(approx):
            quad = approx.reshape(4, 2).astype(np.float32)
            w = np.linalg.norm(quad[0] - quad[1]) + np.linalg.norm(quad[2] - quad[3])
            h = np.linalg.norm(quad[1] - quad[2]) + np.linalg.norm(quad[3] - quad[0])
            r = (w / 2) / (h / 2 + 1e-6)
            if (1.4 <= r <= 2.0) or (0.5 <= r <= 0.72):
                cands.append((quad, box))
        else:
            (_, _), (bw, bh), _ = cv2.minAreaRect(c)
            if min(bw, bh) < 1:
                continue
            r = max(bw, bh) / (min(bw, bh) + 1e-6)
            if 1.4 <= r <= 2.0:
                rect = cv2.boxPoints(cv2.minAreaRect(c)).astype(np.float32)
                cands.append((_order(rect), box))

    # NMS（按面积从大到小）
    cands.sort(key=lambda t: cv2.contourArea(t[0].reshape(-1, 1, 2).astype(np.int32)) if False else -(t[1][2] * t[1][3]))
    kept: list[np.ndarray] = []
    kept_boxes: list[tuple] = []
    for quad, box in cands:
        if all(_iou(box, kb) < 0.3 for kb in kept_boxes):
            kept.append(quad)
            kept_boxes.append(box)

    outs: list[str] = []
    for i, quad in enumerate(kept):
        src = _order(quad)
        w = int((np.linalg.norm(src[0] - src[1]) + np.linalg.norm(src[2] - src[3])) / 2)
        h = int((np.linalg.norm(src[1] - src[2]) + np.linalg.norm(src[3] - src[0])) / 2)
        vertical = h > w
        TW, TH = (600, 1050) if vertical else (1050, 600)
        dst = np.array([[0, 0], [TW, 0], [TW, TH], [0, TH]], dtype=np.float32)
        M = cv2.getPerspectiveTransform(src, dst)
        warp = cv2.warpPerspective(img, M, (TW, TH))
        p = out_dir / f"{stem}_{i}.webp"
        write_image(p, warp, ".webp", 90)
        outs.append(str(p.resolve()))
    return outs
