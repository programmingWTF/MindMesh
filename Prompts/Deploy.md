# Prompts / Deploy.md — 让 Agent 帮你部署

> **用法**：把分隔线之间的内容整段复制给 Agent。按你的实际形态删掉不需要的部分。

---

我要把 MindMesh 用起来。请先问我三个问题，确认后再动手：

1. **形态**：单人（一个仓库）/ 多 Agent / 自建（有常驻机器）？
2. **远端**：GitHub / 其它托管 / 自建 Git 服务？仓库是 private 还是 public？
3. **有几台机器、几个 Agent、分别叫什么名字？**

问完后，按下面的对应部分执行。

---

## A. 单人或多人共用（零服务器）

1. 在远端创建仓库（**默认 private**），克隆到本地固定路径。
2. 按我给的 Agent 名单，为每个名字建 `Memory/<Name>/`，并写入 `.gitkeep`。
3. 在 `AGENTS.md` 第 13 条填入名单（**走 PR，不要直接改 main**）。
4. 提交并推送初始结构。
5. 输出一份「把哪个提示词发给哪个 Agent」的清单。

## B. 定时自检

**优先用 GitHub Actions**（不需要机器）：

- 生成 `.github/workflows/audit.yml`，`cron` 每周一次；
- `actions/checkout` 要带 `fetch-depth: 0`；
- 把 `Scripts/audit.sh` 的输出写进 `GITHUB_STEP_SUMMARY`；
- 如果仓库是 private，注意 Actions 的免费额度。

**如果有常驻机器**：给出 crontab 或 systemd timer 的写法，并说明日志放哪。

## C. 看板（自建时）

1. 设置 `Dashboard/secret/`（`chmod 700`，生成 *摘要* 而不是明文口令）。
2. 用环境变量启动，**默认只监听 `127.0.0.1`**。
3. 告诉我怎么在**先配好鉴权**的前提下对外发布；
   **不要**给我任何具体的 CDN / 隧道 / 代理厂商绑定方案——那部分我自己决定。
4. 检查 `Dashboard/secret/` 确实在 `.gitignore` 里。

## D. 收尾（必做）

- [ ] 跑一次 `bash Scripts/leakscan.sh`，确认没有密钥入库
- [ ] 确认 `main` 分支保护已开（禁止 force push）
- [ ] 确认所有 Agent 的名字在 `AGENTS.md` 与 `Memory/` 中一致
- [ ] 给我一份「下一步该做什么」的三条建议

## 约束

- 任何对 `Skills/`、`docs/`、顶层文档的修改都**走分支 + PR**，不要直接推 main。
- **不要**把任何密钥写进仓库或提交信息。
- 遇到不清楚的地方**停下来问我**，不要自己假设。
