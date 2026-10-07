# 变更日志

本文件记录本项目所有值得注意的变更。
格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [SemVer](https://semver.org/lang/zh-CN/)。

> ⚠️ 说明：本项目**更像一个方向、一个架构，而不是一个产品**。
> 这里的版本号标记的是**文档与参考实现的修订**，不构成任何兼容性承诺。

## [Unreleased]

- 待定

## [v0.1.3] — 2026-10-08

### Changed

- 设计文档目录由 ~~Docs/~~ 改为小写 ~~docs/~~，仓库内所有引用同步更新（~~README~~ / ~~AGENTS.md~~ / ~~Index.md~~ / ~~Prompts~~ / ~~Skills~~ 等）
- 文件名仍保持 **PascalCase**（协议第 2 条），只改目录名

## [v0.1.2] — 2026-10-08

### Added

- **英文 README**：`README.md` 改为英文（面向国际读者），中文版移至 `README.zh.md`
- 两个文件顶部各加一行语言切换器：`< English | [简体中文](./README.zh.md) >` / `< [English](./README.md) | 简体中文 >`
- 英文版新增一节，说明随仓库附带的文档与技能以中文撰写、可按需翻译

### Fixed

- 中文 README 末尾一行被误渲染为代码块

## [v0.1.1] — 2026-10-08

### Added

- 仓库标准化：issue forms、PR 模板、CODEOWNERS、`SECURITY.md`、`CODE_OF_CONDUCT.md`、`VISION.md`、`LABELS.md`
- `.github/workflows/ci.yml`：密钥扫描 + Shell/Python 语法检查 + 命名规范 + 看板可启动性
- 架构图 `docs/Architecture.svg`（并在 README 与 `docs/Architecture.md` 中引用）
- `main` 分支规则集：要求 PR、线性历史、禁止 force push、禁止删除分支
- `AGENTS.md` 补充「项目速览 / 常用命令 / 改动约定 / 最容易踩的三个坑」

## [v0.1.0] — 2026-10-08

### Added

- **协作协议** `AGENTS.md`：20 条，含单写者分区、只读公共区、`git pull --rebase` 第一原则、`Agent:` trailer 规范、密钥红线
- **入口文档**：`SKILL.md`、`00StartHere.md`、`Index.md`、`SkillsList.md`
- **10 个技能**：Memory、SkillForge、Github、Email、Reports、Files、RemoteAccess、WebSearch、Coding、Desktop
- **设计文档**：`Why`、`Architecture`、`Deployment`、`ZeroServer`、`SkillAuthoring`、`Orchestrator`、`Dashboard`、`Faq`
- **4 份 Agent 提示词**：Bootstrap、Deploy、AuthorSkill、Orchestrate
- **5 个治理脚本**：`audit.sh`、`leakscan.sh`、`notify.sh`、`sync.sh`、`check-env.sh`
- **只读看板**：纯 Python 标准库，全环境变量，默认仅监听 `127.0.0.1`，路径前缀分级鉴权
- **模板文档**：`01Environment` / `02Identity` / `03Capabilities` / `04RemoteAccess` / `05Secrets.example` / `06World`
- **CI**：`.github/workflows/audit.yml`（周度审计）
- License：Apache-2.0

### Notes

- 刻意**不提供**任何 CDN / 代理 / 隧道的接入方案
- 刻意**不提供**一键安装脚本
