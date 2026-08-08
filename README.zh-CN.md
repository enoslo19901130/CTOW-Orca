# CTOW — Codex 团队协作治理流程

[English](README.md) | [繁體中文](README.zh-TW.md) | 简体中文

> 版本 0.2.2 · Orca-native 开发模板

CTOW 是一套在 Orca 中运行层级式 Codex 团队的治理流程。它规定谁负责规划、调度、实现、审查与决策；Orca 则是唯一权威的执行 Runtime。

> **兼容性提醒：** Orca orchestration 仍具有版本敏感性且属于实验功能。本文示例以已审查的基准为准，但实际操作应以本机安装的 Orca CLI 帮助与 orchestration skill 为最高依据。CTOW 已具备策略与单元验证，但尚未宣称 CI 中已有自动化真实 Orca E2E 测试。

## CTOW 提供什么

```text
USER → SOL → TERRA → LUNA → RESULT
        规划    调度      实现/测试
```

- **User**：掌握产品意图、约束与 Human Decision。
- **Sol（Architect）**：负责架构、计划、重大决策与最终审查。
- **Terra（Commander）**：负责 Orca Run、Task DAG、Dispatch、集成与 canonical issue identity。
- **Luna（Worker）**：在明确范围内实现、测试与报告。
- **Luna Reviewer**：以不同 session 与 Dispatch 独立审查高风险工作。
- **Orca**：负责 worktree、terminal、Worker、Task、Dispatch 与执行状态。
- **CTOW**：负责治理规则与证据，不取代 Orca Runtime。

决策向下流动，问题与不确定性向上流动：

```text
决策：USER → SOL → TERRA → LUNA
问题：LUNA → TERRA → SOL → USER
```

完整文件访问权不等于完整决策权；每个角色都必须遵守责任边界。

## 为什么需要 CTOW

CTOW 解决的不是“多开几个 Agent”，而是让多人协作可治理、可验证：

- 明确的权责与交接边界；
- 通过 Orca 监督 Worker Dispatch；
- 按依赖关系拆分 Work Package 与 Task；
- 高风险变更采用独立审查；
- 结构化 escalation 与 Human Decision gate；
- 稳定 issue fingerprint 与有界验证，避免相同证据反复消耗 reasoning；
- 使用 schema 与 `ctow-guard` 验证治理产物。

CTOW 不实现 PTY manager、process supervisor、worktree manager、Task database 或第二套执行状态机。详见 [ADR-0001](docs/adr/ADR-0001-ORCA-AUTHORITATIVE-RUNTIME.md)。

## 环境要求与预检

需要 Git、Codex CLI、Orca、Python 3.10+，并在需要时启用 Orca orchestration。

```bash
python -m pip install -e .
python scripts/preflight.py
python scripts/verify_skills.py
```

`config/agents.yaml` 中的 model 名称代表策略意图。必须核对实际 Orca/Codex 报告的 model 与 reasoning effort，不得静默降级。

## 命令入口

所有场景都先按意图选择命令：

```text
查询或接手现有工作 → ctow status
提出全新需求       → ctow-plan "<任务目标>"
启动已批准工作     → ctow-start --plan <PLAN.yaml>
```

查询或接手时，必须先读取权威 Runtime 状态与本地治理进度：

```bash
ctow status
# 等价形式：ctow-status
```

全新需求先创建 planning request：

```bash
ctow-plan "新增 API Key 管理"
```

该命令会保存 planning request 并生成可交给 Sol 的 Prompt。Sol 完成正式 Plan 且验证通过后，可以先预览，再创建权威的 Orca Run：

```bash
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml --dry-run
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml
```

统一形式 `ctow plan`、`ctow start` 与上述命令等价。`ctow-start "<完全一致的目标>"` 只是从 `.ctow/plans/` 找到唯一有效 Plan 的快捷方式，不是跳过规划的许可。命令在交给 Terra 后停止，不创建第二套 scheduler 或 Worker Runtime。详见 [命令入口说明](docs/COMMANDS.md)。

## 如何启动项目

正常入口是 User 向 Sol 提出需求。请提供目标、约束、权威文件、验收条件，以及不可变更的事项。Sol 先完成 discovery 与 planning；批准后的计划再由 Terra 转为 Orca Tasks 并调度 Luna。

### 建议立项信息模板

```yaml
project_goal:
background:
current_state:
desired_state:
must_have:
must_not_change:
known_constraints:
known_risks:
authoritative_documents:
acceptance_criteria:
out_of_scope:
human_decisions_already_made:
notes:
```

不必填写所有字段。可以直接使用以下启动 Prompt：

```text
你现在是本 repository 的 CTOW Sol Architect。

请先读取 AGENTS.md、Sol skill、相关 ADR 与 policy、现有 .ctow/
governance evidence，以及当前 repository 状态。

目标：[描述成果]
约束：[必须或不得改变的事项]
验收：[如何确认完成]

先进行 discovery 与 planning，不要直接 implementation。请定义 scope、risk、
acceptance criteria、Work Package、dependency、execution profile、Worker 需求与
independent review 要求。只有信息缺口会实质改变产品意图、架构边界或验收条件时，
才询问 Human。验证 Plan 后交给 Terra 执行。
```

### 完整执行流程

```text
User 提出需求
  → Sol 探索、架构、风险、验收、Work Package
  → 通过验证的 CTOW Plan
  → Terra 创建 Orca Run、Task DAG、worktree 与 Dispatch
  → Luna 实现、build、test、report
  → 高风险工作由另一个 Luna 独立审查
  → Terra 集成并验收
  → Sol 进行最终架构与计划符合性审查
  → User 收到结果、决策、证据、剩余风险与延期项目
```

## 常见操作场景

### 1. 全新项目

要求 Sol 先定义产品边界、核心 entity、安全性、数据持久化、API/UI 边界、部署假设、风险与验收，再创建 Work Package DAG。适用于尚未建立架构的项目。

### 2. 现有系统新增功能

明确指出受影响领域与不可破坏的 invariant。Sol 先梳理 ownership、transaction 与 compatibility boundary，再规划变更。例如交易功能应明确账号归属、物品一致性、rollback、concurrency 与旧数据兼容性。

### 3. Root cause 未知的间歇性 Bug

不要预先指定修复方法。要求 Sol 建立 failure domain、可证伪 hypothesis、所需 evidence 与成功/失败标准。Terra 可使用 `SWARM`，让最多三个 Luna 沿独立证据路径调查，最后由 Terra 汇总，而不是多数表决。

### 4. Root cause 已知的小型修复

范围小且不涉及架构或 shared contract 时使用 `SMALL`。由一个 Luna 完成 root cause confirmation、最小修复、regression test 与聚焦验证。

### 5. 大型 Refactor

清楚列出不可改变的 invariant，要求拆分成可 build、可恢复、渐进式 Work Package。应明确 protocol behavior、初始化顺序、shared state、兼容性、rollback 与 regression coverage；高风险 package 必须独立审查。

### 6. 用户偏好的方案尚未成为决策

明确标记为 proposed direction。Sol 应独立评估必要性、consistency model、failure mode、运维成本、latency 与更简单的替代方案，不可把偏好直接当作已批准的 architecture requirement。

### 7. 已有完整权威规范

列出 PRD、protocol、schema、API contract 与 acceptance 文件。Sol 应执行 gap analysis 并保持规范意图。只有规范内部矛盾、无法兼容或验收条件互斥时才需要 Human Decision。

### 8. Security 或 Data Integrity 变更

Authentication、authorization、billing、encryption、migration 或 ownership transfer 必须要求 independent review、rollback、regression test、failure-mode analysis、auditability，以及明确的安全/完整性验收条件。

## Execution Profiles

| Profile | Luna 数量 | 适用场景 |
|---|---:|---|
| `SMALL` | 1 | 小型、低风险修复或功能 |
| `MEDIUM` | 2 | 跨模块、中等依赖工作 |
| `FULL` | 3 | 大型功能或多 Work Package refactor |
| `SWARM` | 3 | 对困难未知问题进行独立调查 |

Profile 是调度策略，不是不同 model。`SWARM` 中各 Worker 必须先独立调查，再由 Terra 汇总。详见 [SWARM mode](docs/SWARM-MODE.md)。

## Escalation 与决策进度

Luna 将局部不确定性报告给 Terra；Terra 解决 execution issue，并把 architecture 或 plan conflict 升级给 Sol；Sol 再把产品歧义、破坏性选择或 owner-level trade-off 升级给 User。

Terra 拥有 canonical `issue_fingerprint`，在发送压缩 Decision Brief 前必须查阅 `.ctow/issues/`、`.ctow/decisions/` 与 `.ctow/decision-progress/`。改写措辞、另一位 Worker 同意，或重跑相同测试，都不算新证据。

Sol 只能采取：

- `DECIDE`；
- 要求一次有界的 `REQUEST_TARGETED_EVIDENCE`；
- `REVISE_PLAN`；
- `ESCALATE_HUMAN`。

相同问题与 decision question 在没有 material evidence delta 的情况下进入第 2 cycle 后，不得再次要求 targeted validation。详见 [Decision Efficiency](docs/DECISION-EFFICIENCY.md)、[Fingerprint Policy](docs/FINGERPRINT-POLICY.md) 与 [Decision Progress Ledger](docs/DECISION-PROGRESS-LEDGER.md)。

## 独立审查

高风险工作必须由不同 Luna session 审查：

```text
author_agent != reviewer_agent
author_session != reviewer_session
author_dispatch != reviewer_dispatch
```

Reviewer 开始时取得 Task Contract、acceptance criteria、diff、test result 与 repository evidence，而不是作者完整 reasoning transcript。详见 [Independent Review](docs/INDEPENDENT-REVIEW.md)。

## 验证治理产物

```bash
ctow-guard validate-config
ctow-guard validate-plan examples/PLAN-DEMO.yaml
ctow-guard validate-task examples/TASK-WP001.yaml
ctow-guard validate-worker-report examples/WORKER-REPORT-DEMO.yaml
ctow-guard validate-review examples/REVIEW-DEMO.yaml
ctow-guard validate-issue-identity examples/ISSUE-IDENTITY-DEMO.yaml
ctow-guard validate-escalation examples/ESCALATION-DEMO.yaml
ctow-guard validate-decision examples/DECISION-DEMO.yaml
ctow-guard validate-decision-progress examples/DECISION-PROGRESS-DEMO.yaml
```

## Repository 结构

| 路径 | 用途 |
|---|---|
| `AGENTS.md` | Agent 进入 repository 时的入口规则 |
| `.agents/skills/` | CTOW operator，以及 Sol、Terra、Luna 与独立 Reviewer 的角色契约 |
| `config/` | Agent profile 与治理 policy |
| `.ctow/` | 长期治理证据，不是 Runtime database |
| `docs/adr/` | 架构决策 |
| `docs/` | Workflow、escalation、review、recovery 与 integration 指南 |
| `schemas/`、`examples/` | Governance schema 与有效示例 |
| `src/ctow_guard/`、`tests/` | 验证包与 policy tests |

## 项目状态

CTOW v0.2.2 是经过治理强化的 Orca-native 开发模板，已包含角色契约、策略、schema、示例、Guard 验证与单元测试。下一个里程碑是真实 Orca E2E 证明；在执行 [proof checklist](docs/ORCA-E2E-PROOF.md) 并记录到 [verified baseline](docs/ORCA-VERIFIED-BASELINE.md) 前，不宣称已完成 Runtime E2E 验证。

## 文档导航

- [架构](ARCHITECTURE.md)
- [Workflow](docs/WORKFLOW.md)
- [Orca integration](docs/ORCA-INTEGRATION.md)
- [Task Contract](docs/TASK-CONTRACT.md)
- [命令入口](docs/COMMANDS.md)
- [Issue escalation](docs/ISSUE-ESCALATION.md)
- [Break-glass policy](docs/BREAK-GLASS.md)
- [Changelog](CHANGELOG.md)
