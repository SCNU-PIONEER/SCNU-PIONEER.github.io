# tools

两个离线脚本，只在改图时用得到。运行需要 Python 3、Pillow 与 numpy。

## extract-particles.py

把 `assets/logo.png` 采样成一串带坐标和颜色的点，写进 `assets/particles.js`。

```powershell
python tools/extract-particles.py                 # 默认 --step 9
python tools/extract-particles.py --step 10       # 当前页面使用的密度
python tools/extract-particles.py --preview out   # 顺手导出一张 PNG 预览
```

流程：

1. 用 alpha 通道裁出主体，补成正方形。
2. 按 `step × step` 的格子做面积平均，取 alpha 覆盖率 ≥ 0.22 的格子。
3. 每个格子的颜色量化到调色板里最近的一项（按 RGB 距离加权），同时记下覆盖率。
4. 输出 `{version, count, grid, step, source, palette, data}`，其中 `data` 是
   每个点 4 字节的 base64（`gx, gy, 调色板序号, 覆盖率`），运行时按 stride 抽稀，
   保证不同屏幕上点距一致。

调色板在脚本顶部：左侧是 logo 里取到的原始颜色，右侧是暗色主题下提亮过的颜色
（原始色直接铺在近黑背景上会发闷）。改主题配色时改这里，再跑一次。

采样密度参考：`step 9` → 107×107 网格、7068 点；`step 10` → 97×97 网格、5832 点。

## make-icons.py

从 `assets/particles.js` 渲染出所有静态图片，保证页面、图标、分享卡片用的是同一套颜色。

```powershell
python tools/make-icons.py
```

产出 `assets/icon-64.png`、`assets/icon-180.png`、`assets/emblem-640.png`（无 JS 兜底）与
`assets/og.png`（1200×630 分享卡片）。分享卡片的字标用系统中的 Segoe UI Light，
找不到该字体时会自动省略字标，只保留图案。
