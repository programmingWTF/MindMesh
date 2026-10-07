# MindMesh

< English | [简体中文](./README.zh.md) >

> **Many agents, one mind.**

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](./LICENSE)
[![Status](https://img.shields.io/badge/status-reference%20architecture-orange.svg)](./VISION.md)
[![Server](https://img.shields.io/badge/server-not%20required-brightgreen.svg)](./docs/ZeroServer.md)
[![Agents](https://img.shields.io/badge/agents-any%20of%20them-8a2be2.svg)](./AGENTS.md)
[![Labels](https://img.shields.io/badge/labels-taxonomy-6e7781.svg)](./LABELS.md)

MindMesh is a **Git repository** — it holds your AI partner's **memory**, **skills** and **collaboration protocol**.

Any agent (Claude Code / Codex / Cursor / Copilot / Gemini CLI / one you built yourself…) that picks up this repository
ends up with **roughly the same capabilities, memory and behaviour** — even when their vendors, models and prices differ.

> This is not a plugin, not a service, and not a one-click installer.
> **It is an approach, a direction, an architecture.** Adapt it to your own reality.

![MindMesh architecture](docs/Architecture.svg)

---

## Contents

- [Why you need it](#why-you-need-it)
- [What it gives you](#what-it-gives-you)
- [Up and running in 15 minutes (zero server)](#up-and-running-in-15-minutes-zero-server)
- [Repository layout](#repository-layout)
- [Three shapes](#three-shapes)
- [Let the agent do it](#let-the-agent-do-it)
- [About the "orchestrator"](#about-the-orchestrator)
- [Dashboard](#dashboard)
- [Scope and disclaimers](#scope-and-disclaimers)
- [License](#license)

---

## Why you need it

The reality is: **you will not use just one agent.**

Vendor limits, subscription prices, the things each model happens to be good at, a feature only one of them has,
a free quota that ran out — so you keep three or four agents open, each doing its own thing.

Then you hit three walls:

| Failure mode | Symptom |
|---|---|
| 🧠 **Amnesia** | You switch agents and it doesn't know who you are, what's installed on your machine, or how that last mess got fixed |
| ⚔️ **Write collisions** | Several agents edit the same "memory" at once, overwrite each other, and nobody knows which version is true |
| 🦠 **Context bleed** | Rules, secrets and habits from the last project leak into the next one |

MindMesh solves all three with one unglamorous move:

> **Put the context in a Git repository. Give every agent a memory area only it can write to. Make everything else read-only.**

Unpacked, that is the entire architecture (see `docs/Architecture.md`):

1. **Git is the only synchronisation mechanism.** No database, no API, no MCP, no daemon.
   If an agent can run `git pull`, it can join. **Every agent can already do that.**
2. **Single-writer partitions.** Only one agent can write to `Memory/<AgentName>/`.
   Conflicts become physically impossible — this is the single most important rule in the design.
3. **Pull before you read.** The first step of anything is `git pull --rebase`, **even when all you want to do is read memory**.
   The cost of skipping it isn't a rejected push — it's **making a decision on stale memory**, which is far worse.
4. **Collaborative documents as code.** `Skills/` and the top-level docs go through PRs:
   who changed what, and why, all live in Git history.

---

## What it gives you

| Capability | Where | What it means |
|---|---|---|
| 🧠 **Shared memory** | `Memory/<Agent>/` | A private directory per agent, all inside one repository: greppable, traceable, revertible |
| 🧰 **Shared skills** | `Skills/<Name>/SKILL.md` | Write it once, every agent can use it; changes go through PRs |
| ⚖️ **Shared behaviour** | `AGENTS.md` (repo root) | The constitution: who's who, what you may write, how to commit, what is forbidden |
| 🧭 **Load on demand** | `Index.md` / `SkillsList.md` | Keyword routing, so the whole repo never lands in your context at once |
| 🩺 **Self-auditing** | `Scripts/audit.sh` | Scans for leaked secrets, naming violations, repo size, per-agent activity |
| 📊 **Observable** | `Dashboard/` | A read-only board that visualises commits and memory changes |
| 🤝 **Self-service** | `Prompts/` | Prompts you hand straight to an agent: bootstrap, deploy, author skills, orchestrate |

---

## Up and running in 15 minutes (zero server)

You need exactly **one Git remote**. **GitHub is enough** — no server, no domain, no Docker.

### 1. Create the repository

Fork this repo, or copy it as a template, into your own account (keep it **private** at first; you can open it later).
Name it anything, e.g. `my-mindmesh`.

### 2. Clone it

```bash
git clone git@github.com:<you>/<your-mindmesh>.git
cd <your-mindmesh>
```

### 3. Give every agent a name

Name = memory directory = commit author = `Agent:` trailer. **All of them must match exactly.**

```bash
mkdir -p Memory/ClaudeCode Memory/Codex
touch Memory/ClaudeCode/.gitkeep Memory/Codex/.gitkeep
```

### 4. Hand the entry point to your agent

Point it at `AGENTS.md` and `00StartHere.md` in the repository root.
Or simpler: paste it the prompt from `Prompts/Bootstrap.md`.

### 5. Let it work, commit, push

```bash
git add -A Memory/ClaudeCode && git commit -m "ClaudeCode: today's progress

Agent: ClaudeCode"
git push
```

### 6. Add another agent and repeat steps 3–5

Now they share the same skills, the same rules, and the same knowledge about you.

> 📖 More deployment detail (multi-machine, multi-user, private remotes, self-hosted Git) → `docs/Deployment.md`.
> 📖 **No server at all?** → `docs/ZeroServer.md` — use GitHub as the remote and GitHub's own pages as the front end.

---

## Repository layout

```text
MindMesh/
├── README.md              Front page for humans (English)
├── README.zh.md           Front page for humans (简体中文)
├── AGENTS.md              ⭐ Collaboration protocol / the constitution (read this first)
├── CLAUDE.md              Short pointer to the protocol (auto-loaded by Claude Code)
├── SKILL.md               This repository as one big Skill
├── 00StartHere.md         The 8 steps for a brand-new agent
├── Index.md               Keyword routing table (don't read it all)
├── SkillsList.md          Full skill inventory
├── 01Environment.md       Machine environment (template)
├── 02Identity.md          Persona and tone (template)
├── 03Capabilities.md      Capability matrix
├── 04RemoteAccess.md      Remotes / SSH / servers
├── 05Secrets.example.md   Credential field list (names only, no values)
├── 06World.md             Your world: devices / network / people (template)
├── docs/                  Why, architecture, deployment, authoring, orchestrator, dashboard
├── Prompts/               Prompts to hand to agents
├── Skills/                Skill library (write once, every agent uses it)
├── Memory/                Private memory per agent (single-writer partitions)
├── Scripts/               Governance scripts: audit / leak scan / notify / sync
├── Dashboard/             Read-only activity board (self-hostable)
├── Credentials/           🚫 gitignored, never committed
└── .gitignore
```

**Naming**: managed files and directories use **PascalCase** (capitalised words, no spaces, no hyphens, no underscores).
A few fixed names must never change: `AGENTS.md` `CLAUDE.md` `SKILL.md` `README.md`, and date files of the form `YYYY-MM-DD.md`.

> ⚠️ The bundled documents and skills are written in Chinese. The architecture is language-agnostic —
> if you need them in another language, have an agent translate them and commit the result.

---

## Three shapes

Don't adopt everything on day one. Pick by what you actually have:

| Shape | You need | You get |
|---|---|---|
| **① Solo** | One GitHub repository | Memory that survives, an agent that doesn't forget you |
| **② Multi-agent** | The same repository + one credential per agent | No collisions, one skill set, full traceability |
| **③ Self-hosted** | An always-on machine / NAS / small VPS | All of the above, plus a dashboard, scheduled audits and a private remote |

**Most people only need ①.** ③ is for people who have already hit a ceiling.

---

## Let the agent do it

`Prompts/` contains prompts written for agents, not documentation written for humans. Paste the whole block:

| Prompt | Purpose |
|---|---|
| `Prompts/Bootstrap.md` | Have a brand-new agent read the protocol and join |
| `Prompts/Deploy.md` | Have an agent deploy the repository / dashboard / scheduled jobs for you |
| `Prompts/AuthorSkill.md` | Have an agent **design a new skill** and open a PR |
| `Prompts/Orchestrate.md` | Have an agent act as **maintainer** (audit, review PRs, sync) |

The design principle is simple: **anything an agent can do should not be written into a document for humans.**

---

## About the "orchestrator"

The repository has a **maintainer** role: periodic audits, reviewing skill PRs, running leak scans, syncing upstream.

**It does not have to be any particular agent.**

Anything that can do the following qualifies:

- run shell commands (the scripts in `Scripts/`)
- do **scheduled / recurring work** (cron, systemd timers, GitHub Actions, a platform heartbeat)
- operate Git (commit, open PRs, merge)

So it can be Claude Code, it can be Codex, it can be a purpose-built script agent,
and it can even be **GitHub Actions** — at which point you don't need an "agent" at all.

> ⚠️ But remember: **the maintainer is a replaceable executor; `AGENTS.md` is the authority.**
> If one agent is both player and referee, split auditing and merging away from it.

See `docs/Orchestrator.md`.

---

## Dashboard

`Dashboard/` is a **read-only** static service plus a small Python HTTP server:

- lists every agent's commits and memory changes
- lets you browse the repository's Markdown in a browser (gated by public / private path prefixes)
- never writes to the repository and never touches files — it reads using **Git query commands only**

It listens on `127.0.0.1` by default and ships with **no reverse proxy / CDN / tunnel configuration whatsoever**.
To publish it, add your own layer in nginx / Caddy — **and configure authentication first**.

> 🔒 We **deliberately do not ship** Cloudflare-style proxying, CDN or tunnel integrations.
> Those are vendor-specific bindings and do not belong inside a neutral design. Use whatever you like.

See `docs/Dashboard.md`.

---

## Scope and disclaimers

**This is a reference implementation, not a product.**

- ❌ No one-click installer (you can have an agent follow `Prompts/Deploy.md` instead)
- ❌ No compatibility guarantees, no SLA, no hosted service
- ❌ No promise it fits your situation — **treat it as homework you can copy, not a distribution you can run**
- ⚠️ It contains **no secrets**; please don't commit yours (`Scripts/leakscan.sh` is a safety net, not a guarantee)
- ⚠️ In a public repository, `Memory/` **is public**. Keep private notes in a private repo, or split them out.

**It is closer to a thinking pattern, a direction, an architecture — than to a fixed artifact.**

---

## License

[Apache-2.0](./LICENSE) © 2026 programmingWTF

---

> **MindMesh** — memory and skills shouldn't belong to a single agent.
