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
assets/logo.png            原始标识，同时用作浏览器标签图标
assets/particles.js        从 logo 采样出的粒子数据（base64，约 31 KB）
assets/emblem-640.png      无 JS 时的静态图案
assets/og.png              分享卡片 1200×630
tools/extract-particles.py 从 logo 生成粒子数据
tools/make-icons.py        生成静态图案与分享卡片
```

## 交互

| 操作 | 效果 |
| --- | --- |
| 指针进入页面 | 图案中心向外逐点浮现 |
| 指针靠近光点 | 光点被吸附，绕着指针旋进，中心让出一个小空洞，外圈挤压成更密的环 |
| 指针离开 | 光点按弹簧模型回到各自位置 |
| 触摸 | 与鼠标一致，抬起后归位 |
| 系统「减少动态效果」 | 只渲染一帧静态图案 |

静止时页面不再重绘（`requestAnimationFrame` 仍在跑，但只做物理计算），指针移开、光点归位后画面就停在那一帧，所以空闲时几乎不耗电。

## 可调参数

全部集中在 `js/main.js` 顶部的 `CFG` 对象里，改完刷新即可：

| 参数 | 默认 | 含义 |
| --- | --- | --- |
| `maxSize` | `700` | 图案长边上限，css px |
| `pitch` | `7.2` | 屏幕上相邻光点的目标间距 |
| `dot` | `1.42` | 光点实心半径 |
| `halo` | `2.15` | 光晕半径，相对实心半径的倍数 |
| `influence` | `0.26` | 磁力作用半径，占图案长边的比例 |
| `pull` | `1.05` | 吸附强度，越大吸得越狠 |
| `swirl` | `0.38` | 旋进比例，`0` 只吸入、越大越绕圈 |
| `shell` | `0.042` | 指针周围的排斥圈半径 |
| `repel` | `3.0` | 排斥强度，防止光点塌成一点 |
| `spring` | `0.015` | 回位弹力 |
| `damping` | `0.905` | 阻尼，越接近 1 越滑 |
| `wander` | `0` | 静止漂移；设成 `0.6` 之类的值会有轻微呼吸感，但页面不再静止 |
| `maxSpeed` | `15` | 每帧速度上限 |
| `pixels` | `4.2e6` | 画布像素预算，超出时自动降 `devicePixelRatio` |

不想改文件也可以直接在控制台里试：

```js
SCNU_PIONEER.cfg                      // 当前全部参数
SCNU_PIONEER.apply({ pull: 1.6 })     // 改几个，立刻重新排版
SCNU_PIONEER.stats()                  // { dots, stride, coarse, dpr, size }
```

页面帧率不够时会自动降级：先降画布分辨率（`pixels`），再隔点抽样（`coarse`），
`SCNU_PIONEER.stats()` 里能看到当前的 `dpr` 与 `coarse`。

## 重新生成资源

改 logo 后，需要重跑两个脚本（Python 3 + Pillow + numpy）：

```powershell
python tools/extract-particles.py --step 10   # logo -> assets/particles.js
python tools/make-icons.py                    # -> 静态图案 / 分享卡片
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
