# CTOW — Codex 團隊協作治理流程

[English](README.md) | 繁體中文 | [简体中文](README.zh-CN.md)

> 版本 0.2.2 · Orca-native 開發範本

CTOW 是一套在 Orca 中運作階層式 Codex 團隊的治理流程。它規範誰負責規劃、排程、實作、審查與決策；Orca 則是唯一具權威性的執行 Runtime。

> **相容性提醒：** Orca orchestration 仍具版本敏感性且屬實驗性功能。本文範例以已審查的基準為準，但實際操作應以本機安裝的 Orca CLI 說明與 orchestration skill 為最高依據。CTOW 已具備政策與單元驗證，但尚未宣稱 CI 中已有自動化真實 Orca E2E 測試。

## CTOW 提供什麼

```text
USER → SOL → TERRA → LUNA → RESULT
        規劃    排程      實作/測試
```

- **User**：掌握產品意圖、限制與 Human Decision。
- **Sol（Architect）**：負責架構、計畫、重大決策與最終審查。
- **Terra（Commander）**：負責 Orca Run、Task DAG、Dispatch、整合與 canonical issue identity。
- **Luna（Worker）**：在明確範圍內實作、測試與回報。
- **Luna Reviewer**：以不同 session 與 Dispatch 獨立審查高風險工作。
- **Orca**：負責 worktree、terminal、Worker、Task、Dispatch 與執行狀態。
- **CTOW**：負責治理規則與證據，不取代 Orca Runtime。

決策向下流動，問題與不確定性向上流動：

```text
決策：USER → SOL → TERRA → LUNA
問題：LUNA → TERRA → SOL → USER
```

完整檔案存取權不等於完整決策權；每個角色都必須守住責任邊界。

## 為什麼需要 CTOW

CTOW 解決的不是「多開幾個 Agent」，而是讓多人協作可治理、可驗證：

- 明確的權責與交接界線；
- 透過 Orca 監督 Worker Dispatch；
- 依相依關係拆分 Work Package 與 Task；
- 高風險變更採用獨立審查；
- 結構化 escalation 與 Human Decision gate；
- 穩定 issue fingerprint 與有界驗證，避免相同證據反覆消耗 reasoning；
- 使用 schema 與 `ctow-guard` 驗證治理產物。

CTOW 不實作 PTY manager、process supervisor、worktree manager、Task database 或第二套執行狀態機。詳見 [ADR-0001](docs/adr/ADR-0001-ORCA-AUTHORITATIVE-RUNTIME.md)。

## 環境需求與預檢

需要 Git、Codex CLI、Orca、Python 3.10+，並在需要時啟用 Orca orchestration。

```bash
python -m pip install -e .
python scripts/preflight.py
python scripts/verify_skills.py
```

`config/agents.yaml` 中的 model 名稱代表政策意圖。必須核對實際 Orca/Codex 回報的 model 與 reasoning effort，不得靜默降級。

## 指令入口

所有情境都先依意圖選擇指令：

```text
查詢或接手既有工作 → ctow status
提出全新需求       → ctow-plan "<任務目標>"
啟動核准工作       → ctow-start --plan <PLAN.yaml>
```

查詢或接手時，必須先讀取權威 Runtime 狀態與本地治理進度：

```bash
ctow status
# 等價形式：ctow-status
```

全新需求先建立 planning request：

```bash
ctow-plan "新增 API Key 管理"
```

此指令會保存 planning request 並產生可交給 Sol 的 Prompt。Sol 完成正式 Plan 且驗證通過後，可先預覽，再建立具權威性的 Orca Run：

```bash
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml --dry-run
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml
```

統一形式 `ctow plan`、`ctow start` 與上述指令等價。`ctow-start "<完全一致的目標>"` 只是從 `.ctow/plans/` 找出唯一有效 Plan 的捷徑，不是跳過規劃的許可。指令在交給 Terra 後停止，不建立第二套 scheduler 或 Worker Runtime。詳見 [指令入口說明](docs/COMMANDS.md)。

## 如何啟動專案

正常入口是 User 向 Sol 提出需求。請提供目標、限制、權威文件、驗收條件，以及不可變更的事項。Sol 先完成 discovery 與 planning；核准計畫再由 Terra 轉為 Orca Tasks 並調度 Luna。

### 建議開案資訊模板

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

不必填滿所有欄位。可直接使用以下開案 Prompt：

```text
你現在是本 repository 的 CTOW Sol Architect。

請先讀取 AGENTS.md、Sol skill、相關 ADR 與 policy、既有 .ctow/
governance evidence，以及目前 repository 狀態。

目標：[描述成果]
限制：[必須或不得改變的事項]
驗收：[如何確認完成]

先進行 discovery 與 planning，不要直接 implementation。請定義 scope、risk、
acceptance criteria、Work Package、dependency、execution profile、Worker 需求與
independent review 要求。只有資訊缺口會實質改變產品意圖、架構邊界或驗收條件時，
才詢問 Human。驗證 Plan 後交由 Terra 執行。
```

### 完整執行流程

```text
User 提出需求
  → Sol 探索、架構、風險、驗收、Work Package
  → 通過驗證的 CTOW Plan
  → Terra 建立 Orca Run、Task DAG、worktree 與 Dispatch
  → Luna 實作、build、test、report
  → 高風險工作由另一個 Luna 獨立審查
  → Terra 整合並驗收
  → Sol 進行最終架構與計畫符合性審查
  → User 收到結果、決策、證據、剩餘風險與延後項目
```

## 常見操作情境

### 1. 全新專案

要求 Sol 先定義產品邊界、核心 entity、安全性、資料保存、API/UI 邊界、部署假設、風險與驗收，再建立 Work Package DAG。適用於尚未建立架構的專案。

### 2. 既有系統新增功能

明確指出受影響領域與不可破壞的 invariant。Sol 先盤點 ownership、transaction 與 compatibility boundary，再規劃變更。例如交易功能應明列帳號歸屬、物品一致性、rollback、concurrency 與舊資料相容性。

### 3. Root cause 未知的間歇性 Bug

不要先指定修法。要求 Sol 建立 failure domain、可證偽 hypothesis、所需 evidence 與成功/失敗判準。Terra 可使用 `SWARM`，讓最多三個 Luna 沿獨立證據路徑調查，最後由 Terra 統整，而不是多數決。

### 4. Root cause 已知的小型修復

範圍小且不涉及架構或 shared contract 時使用 `SMALL`。由一個 Luna 完成 root cause confirmation、最小修復、regression test 與聚焦驗證。

### 5. 大型 Refactor

清楚列出不可改變的 invariant，要求拆成可 build、可回復、漸進式 Work Package。應明列 protocol behavior、初始化順序、shared state、相容性、rollback 與 regression coverage；高風險 package 必須獨立審查。

### 6. 使用者偏好的方案尚未成為決策

明確標示為 proposed direction。Sol 應獨立評估必要性、consistency model、failure mode、維運成本、latency 與較簡單替代方案，不可把偏好直接當成核准的 architecture requirement。

### 7. 已有完整權威規格

列出 PRD、protocol、schema、API contract 與 acceptance 文件。Sol 應執行 gap analysis 並保持規格意圖。只有規格內部矛盾、無法相容或驗收條件互斥時才需要 Human Decision。

### 8. Security 或 Data Integrity 變更

Authentication、authorization、billing、encryption、migration 或 ownership transfer 必須要求 independent review、rollback、regression test、failure-mode analysis、auditability，以及明確的安全/完整性驗收條件。

## Execution Profiles

| Profile | Luna 數量 | 適用情境 |
|---|---:|---|
| `SMALL` | 1 | 小型、低風險修復或功能 |
| `MEDIUM` | 2 | 跨模組、中等相依工作 |
| `FULL` | 3 | 大型功能或多 Work Package refactor |
| `SWARM` | 3 | 對困難未知問題進行獨立調查 |

Profile 是排程政策，不是不同 model。`SWARM` 中各 Worker 必須先獨立調查，再由 Terra 統整。詳見 [SWARM mode](docs/SWARM-MODE.md)。

## Escalation 與決策進度

Luna 將局部不確定性回報 Terra；Terra 解決 execution issue，並把 architecture 或 plan conflict 升級給 Sol；Sol 再把產品歧義、破壞性選擇或 owner-level trade-off 升級給 User。

Terra 擁有 canonical `issue_fingerprint`，在送出壓縮 Decision Brief 前必須查閱 `.ctow/issues/`、`.ctow/decisions/` 與 `.ctow/decision-progress/`。改寫措辭、另一位 Worker 同意，或重跑相同測試，都不算新證據。

Sol 只能採取：

- `DECIDE`；
- 要求一次有界的 `REQUEST_TARGETED_EVIDENCE`；
- `REVISE_PLAN`；
- `ESCALATE_HUMAN`。

相同問題與 decision question 在沒有 material evidence delta 的情況下進入第 2 cycle 後，不得再次要求 targeted validation。詳見 [Decision Efficiency](docs/DECISION-EFFICIENCY.md)、[Fingerprint Policy](docs/FINGERPRINT-POLICY.md) 與 [Decision Progress Ledger](docs/DECISION-PROGRESS-LEDGER.md)。

## 獨立審查

高風險工作必須由不同 Luna session 審查：

```text
author_agent != reviewer_agent
author_session != reviewer_session
author_dispatch != reviewer_dispatch
```

Reviewer 起始取得 Task Contract、acceptance criteria、diff、test result 與 repository evidence，而不是作者完整 reasoning transcript。詳見 [Independent Review](docs/INDEPENDENT-REVIEW.md)。

## 驗證治理產物

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

## Repository 結構

| 路徑 | 用途 |
|---|---|
| `AGENTS.md` | Agent 進入 repository 時的入口規則 |
| `.agents/skills/` | CTOW operator，以及 Sol、Terra、Luna 與獨立 Reviewer 的角色契約 |
| `config/` | Agent profile 與治理 policy |
| `.ctow/` | 長期治理證據，不是 Runtime database |
| `docs/adr/` | 架構決策 |
| `docs/` | Workflow、escalation、review、recovery 與 integration 指南 |
| `schemas/`、`examples/` | Governance schema 與有效範例 |
| `src/ctow_guard/`、`tests/` | 驗證套件與 policy tests |

## 專案狀態

CTOW v0.2.2 是經治理強化的 Orca-native 開發範本，已包含角色契約、政策、schema、範例、Guard 驗證與單元測試。下一個里程碑是真實 Orca E2E 證明；在執行 [proof checklist](docs/ORCA-E2E-PROOF.md) 並記錄至 [verified baseline](docs/ORCA-VERIFIED-BASELINE.md) 前，不宣稱已完成 Runtime E2E 驗證。

## 文件導覽

- [架構](ARCHITECTURE.md)
- [Workflow](docs/WORKFLOW.md)
- [Orca integration](docs/ORCA-INTEGRATION.md)
- [Task Contract](docs/TASK-CONTRACT.md)
- [指令入口](docs/COMMANDS.md)
- [Issue escalation](docs/ISSUE-ESCALATION.md)
- [Break-glass policy](docs/BREAK-GLASS.md)
- [Changelog](CHANGELOG.md)
