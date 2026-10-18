# SCNU PIONEER

> 一个只放一枚标识的页面。

整页只有一幅居中的粒子图案。图案由 logo 采样出的彩色光点组成，指针靠近时会像磁铁一样把周围的光点吸附、卷拢，移开后它们各自弹回原位。

- 页面：<https://scnu-pioneer.github.io/>
- 页面结构：`index.html` + `css/style.css` + `js/main.js`，无框架、无构建步骤、无外部请求。

## 本地预览

直接双击 `index.html` 即可，所有资源都是相对路径，`file://` 下也能正常运行
（粒子数据是编译期生成的 `assets/particles.js`，不依赖 `fetch` / `getImageData`，因此不存在跨域限制）。

也可以起一个静态服务器：

```powershell
python -m http.server 8000
# 然后打开 http://localhost:8000
```

## 目录

```
index.html                 页面骨架
css/style.css              背景、布局、动效降级
js/main.js                 粒子引擎（解码 / 采样 / 物理 / 绘制）
assets/logo.png            原始标识
assets/particles.js        从 logo 采样出的粒子数据（base64，约 31 KB）
assets/emblem-640.png      无 JS 时的静态图案
assets/icon-64.png         站点图标
assets/icon-180.png        iOS 主屏图标
assets/og.png              分享卡片 1200×630
tools/extract-particles.py 从 logo 生成粒子数据
tools/make-icons.py        生成图标、静态图案与分享卡片
```

## 交互

| 操作 | 效果 |
| --- | --- |
| 指针进入页面 | 图案中心向外逐点浮现 |
| 指针靠近光点 | 光点被吸附，绕着指针旋进，中心让出一个小空洞，外圈挤压成更密的环 |
| 指针离开 | 光点按弹簧模型回到各自位置 |
| 触摸 | 与鼠标一致，抬起后归位 |
| 系统「减少动态效果」 | 只渲染一帧静态图案 |

## 重新生成资源

改 logo 后，需要重跑两个脚本（Python 3 + Pillow + numpy）：

```powershell
python tools/extract-particles.py --step 10   # logo -> assets/particles.js
python tools/make-icons.py                    # -> icon / fallback / og
```

`--step` 是采样网格的边长（源图像素）：数值越小点越密、图案越细腻，文件也越大。
当前 971 px 的源图配 `--step 10`，得到 97×97 网格、5832 个有效点。

## 部署

仓库即站点：GitHub Pages 从 `main` 分支根目录发布，推送即生效。

```powershell
git add -A
git commit -m "..."
git push
```
