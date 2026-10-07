---
name: mindmesh-skillforge
description: 设计、审查、安装一个技能（SKILL.md）。当需要新增能力、把重复流程固化、或从外部安装技能前做安全审查时使用。
---

# 技能锻造

## 该不该写成技能

按顺序问：

| 问题 | 是 | 否 |
|---|---|---|
| 我原生就会吗？ | 直接用原生，**别写** | 继续 |
| 会重复用（≥3 次）吗？ | 继续 | 放 `Memory/` |
| 别的 Agent 也需要吗？ | 继续 | 放 `Memory/` |
| 有明确成功判据吗？ | 写成 `Skills/<Name>/SKILL.md` | 先别写 |

## 结构

```markdown
---
name: <唯一短横线名>
description: <什么时候用它——必须含触发词>
---

# <名字>

## 什么时候用
## 前置条件
## 怎么做
## 命令
## 失败怎么办
## 验证
```

**description 决定它会不会被用到。**把用户可能会说的**原话**写进去。

> 详细写作纪律见 `Docs/SkillAuthoring.md`。

## 安装第三方技能前：安全审查

技能是「**会被信任并执行**」的东西，**它的权限就是你的权限**。

| 检查 | 危险信号 |
|---|---|
| 读什么 | ``` ~/.ssh ```、`.env`、Cookie、凭据管理器 |
| 发什么 | 向未说明的域名 POST |
| 要什么 | `sudo`、关闭安全设置、`--dangerously-*` |
| 藏什么 | 混淆代码、大段 base64、远端拉取后 `eval` |

**任何一条命中 → 不要装。**

```bash
# 快速看一个技能会碰什么
grep -rInE 'curl|wget|POST|ssh|token|password|eval|base64' Skills/<Name>/
```

## 提交流程

```bash
git pull --rebase
git checkout -b add-skill/<名字>      # 改已有技能用 skill/<名字>
git add Skills/<Name>
git commit -m "add-skill: <名字>

Agent: <我的名字>"
git push -u origin add-skill/<名字>
gh pr create --fill
```

**同时更新 `SkillsList.md`（另开 PR，不要混在一起）。**

## 失败路径

| 症状 | 做法 |
|---|---|
| 技能写完了但从不被触发 | `description` 里缺触发词——补上用户会说的原话 |
| 别的 Agent 跑不通 | 你硬编码了本机路径/别名 → 改成环境变量，或标注 ⚠️ |
| PR 被要求修改 | 通常是缺「失败怎么办」或「验证」两节 |

## 验证

- 换一个**没用过这个技能的 Agent**，只给它 `SKILL.md`，问它「你会怎么做」——它能复述出来；
- `SkillsList.md` 里有它的条目；
- `bash Scripts/audit.sh` 的命名检查通过。
