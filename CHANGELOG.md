# 变更日志

本文件记录本项目所有值得注意的变更。
格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

> ⚠️ 说明：本项目**更像一个方向、一个架构，而不是一个产品**。
> 这里的版本号标记的是**文档与参考实现的修订**，不构成任何兼容性承诺。

## [Unreleased]

- 待定

## [v0.1.0] — 2026-10-08

### Added

- **协作协议** `AGENTS.md`：20 条，含单写者分区、只读公共区、`git pull --rebase` 第一原则、`Agent:` trailer 规范、密钥红线
- **入口文档**：`SKILL.md`、`00StartHere.md`、`Index.md`、`SkillsList.md`
- **10 个技能**：Memory、SkillForge、Github、Email、Reports、Files、RemoteAccess、WebSearch、Coding、Desktop
- **7 篇设计文档**：`Why`、`Architecture`、`Deployment`、`ZeroServer`、`SkillAuthoring`、`Orchestrator`、`Dashboard`、`Faq`
- **4 份 Agent 提示词**：Bootstrap、Deploy、AuthorSkill、Orchestrate
- **5 个治理脚本**：`audit.sh`、`leakscan.sh`、`notify.sh`、`sync.sh`、`check-env.sh`
- **只读看板**：纯 Python 标准库，全环境变量，默认仅监听 `127.0.0.1`，路径前缀分级鉴权
- **模板文档**：`01Environment` / `02Identity` / `03Capabilities` / `04RemoteAccess` / `05Secrets.example` / `06World`
- **CI**：`.github/workflows/audit.yml`（周度审计）
- License：Apache-2.0

### Notes

- 刻意**不提供**任何 CDN / 代理 / 隧道的接入方案
- 刻意**不提供**一键安装脚本

## [v0.1.1] — 2026-10-08

### Added

- 仓库标准化：issue forms、PR 模板、CODEOWNERS、`SECURITY.md`、`CODE_OF_CONDUCT.md`、`VISION.md`、`LABELS.md`
- `.github/workflows/ci.yml`：泄漏扫描 + 语法检查 + 看板可启动性
- 架构图 `Docs/Architecture.svg`
- `main` 分支规则集（要求 PR、禁止 force push、禁止删除）
