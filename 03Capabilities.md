# 03Capabilities.md — 能力总表

> 一眼看清「这个组合能干什么、由谁干、做完了算什么」。
> 新增技能后请同步更新本文件与 `SkillsList.md`。

---

## 能力矩阵

| 能力 | 技能 | 需要什么 | 产出 |
|---|---|---|---|
| 记忆读写与召回 | `Skills/Memory` | 无 | 记忆文件 / 结论 |
| 设计一个新技能 | `Skills/SkillForge` | 无 | `Skills/<Name>/SKILL.md` |
| GitHub 协作 | `Skills/Github` | `gh` + token | PR / issue / 合并 |
| 收发邮件 | `Skills/Email` | 邮箱服务凭据 | 已发送 / 已归档 |
| 长报告与发布 | `Skills/Reports` | 静态站点（可无） | HTML / 链接 |
| 文件交付 | `Skills/Files` | 一个投递目录 | 文件 + 可访问路径 |
| 远端机器操作 | `Skills/RemoteAccess` | SSH + 别名 | 命令输出 |
| 检索与调研 | `Skills/WebSearch` | 一般无需 key | 结论 + 出处 |
| 委派编码 | `Skills/Coding` | 一个编码 Agent | 代码 / PR |
| 桌面控制 | `Skills/Desktop` | 图形环境 + 权限 | 截图 / 操作结果 |

---

## 能力分级

| 级别 | 含义 |
|---|---|
| 🟢 **随时可用** | 无外部依赖，任何 Agent 立刻能跑 |
| 🟡 **需要配置** | 需要一次性的凭据 / 路径 / 别名设置 |
| 🔴 **环境受限** | 依赖特定平台、图形环境或付费额度 |

> 请在你自己的 fork 里，把上表加上级别标注。**这是给新 Agent 最重要的提示。**

---

## 明确做不到的事

把「做不到」写下来，和「做得到」一样重要：

- `<例：不能访问需要登录的内部系统>`
- `<例：不能在没有图形界面的机器上截屏>`
- `<例：不代替用户做需要身份/合同的对外承诺>`

---

## 想加一个能力？

1. 交给 `Skills/SkillForge/SKILL.md` 的判断流程；
2. 值得共享 → 写 `Skills/<Name>/SKILL.md` + 开 PR；
3. 只对自己有用 → 放 `Memory/<你的名字>/`；
4. 加完更新本文件与 `SkillsList.md`。
