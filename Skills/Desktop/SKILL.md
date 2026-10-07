---
name: mindmesh-desktop
description: 桌面与图形界面操作：截图、鼠标键盘、窗口、自动化 GUI。当需要看屏幕、点击、输入、操作图形程序时使用。
---

# 桌面控制

## 什么时候需要它

| 场景 | 需要吗 |
|---|---|
| 有 CLI / API 能做 | ❌ **不要用 GUI 自动化** |
| 只有图形界面 | ✅ 用它 |
| 需要「看一眼」确认状态 | ✅ 截图 |
| 需要登录一个没有 API 的网站 | ✅ 浏览器自动化（见 `Skills/WebSearch`） |

> **原则：能用命令行的，绝不用鼠标。**GUI 自动化是最脆弱的一层。

## 截图

```bash
# Linux（有图形环境）
gnome-screenshot -f /tmp/shot.png
# 或
import -window root /tmp/shot.png      # ImageMagick

# macOS
screencapture -x /tmp/shot.png

# Windows（PowerShell）
powershell -c "Add-Type -AssemblyName System.Windows.Forms; \
  [System.Windows.Forms.Screen]::PrimaryScreen | Out-Null; \
  $b=[System.Drawing.Bitmap]::new([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, \
  [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); \
  [System.Drawing.Graphics]::FromImage($b).CopyFromScreen(0,0,0,0,$b.Size); \
  $b.Save('/tmp/shot.png')"
```

> 这个技能只有在**有图形会话**的机器上才成立。服务器上没有 —— 在失败处理里写清楚，别硬试。

## 操作

按可得的工具选一种，并在本技能里**写清你实际用的是哪个**：

| 平台 | 常见手段 |
|---|---|
| Windows | PowerShell + `user32.dll`（鼠标/键盘）、UIAutomation |
| macOS | `osascript`、`cliclick` |
| Linux | `xdotool`、`wmctrl`、`ydotool`（Wayland） |

## 纪律

1. **动之前先截图。**知道当前状态，再决定点哪。
2. **一步一验证。**每次点击/输入后重新截图确认。GUI 没有返回值，**截图就是你的返回值**。
3. **坐标是相对的。**分辨率/缩放变了，硬编码的坐标就废了——优先按**元素**定位，而不是像素。
4. **不要操作不可逆的东西**（删除、付款、发布），除非用户明确要求。
5. **不要在用户不知情时控制他的屏幕。**这是侵入性很强的能力。

## 失败路径

| 症状 | 原因 | 做法 |
|---|---|---|
| `cannot open display` | 没有图形会话 / 在 SSH 里 | 说明无法执行，**不要**尝试伪造 |
| 点击没反应 | 坐标错了 / 窗口未聚焦 | 重新截图，先聚焦窗口 |
| 文字输入乱码 | 输入法 / 编码 | 改用剪贴板粘贴 |
| 分辨率变化后全乱 | 硬编码坐标 | 改成按元素定位 |

## 验证

- 每次操作后**截图对比**，确认状态真的变了；
- 结束时给用户一张最终截图，而不是一句「已完成」。
