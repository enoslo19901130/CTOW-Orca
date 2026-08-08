# CTOW 專案啟動與 Sol 開案情境指南

> 適用基準：CTOW v0.2.2  
> 定位：Orca-native Codex Team Orchestration Workflow  
> 目的：說明如何從「使用者提出需求」開始，由 Sol 建立計畫，再交由 Terra 與 Luna 完成專案執行。

---

## 1. 文件目的

本文件用來說明在 CTOW 架構下，使用者應如何啟動一個專案、如何與 Sol 互動，以及不同情境下應該如何描述需求。

CTOW 的核心不是讓使用者自己管理多個 Agent，而是建立明確的責任鏈：

```text
USER
  │
  │ Goal / Constraint / Human Decision
  ▼
SOL
Architect
GPT-5.6 Sol / MAX / Fast OFF
  │
  │ Approved Plan
  ▼
TERRA
Commander
GPT-5.6 Terra / HIGH / Fast OFF
  │
  │ Task DAG / Scheduling / Worker Dispatch
  ▼
LUNA
Worker
GPT-5.6 Luna / MAX / Fast OFF
  │
  │ Implementation / Build / Test / Report
  ▼
Project Result
```

基本原則：

- **User 控制目標與最終產品意圖**
- **Sol 控制架構、計畫與重大決策**
- **Terra 控制執行排程、Task DAG 與 Worker 調度**
- **Luna 負責實際工程執行**
- **Orca 是 Execution State 的唯一真相來源**
- **`.ctow/` 僅保存 Governance Evidence**
- **問題向上流動，決策向下流動**
- **不得因同一批證據反覆重驗而浪費高 reasoning token**

---

## 2. 專案開始前的基本條件

建議專案 repository 至少具備：

```text
Project/
├── AGENTS.md
├── .agents/
│   └── skills/
│       ├── ctow-operator/
│       │   └── SKILL.md
│       ├── ctow-sol-architect/
│       │   └── SKILL.md
│       ├── ctow-terra-commander/
│       │   └── SKILL.md
│       ├── ctow-luna-worker/
│       │   └── SKILL.md
│       └── ctow-luna-independent-reviewer/
│           └── SKILL.md
├── .ctow/
│   ├── requests/
│   ├── plans/
│   ├── issues/
│   ├── escalations/
│   ├── decisions/
│   ├── decision-progress/
│   ├── reviews/
│   ├── human-decisions/
│   └── audits/
│       └── break-glass/
└── project source files...
```

Sol 啟動時應先理解：

1. `AGENTS.md`
2. `ctow-sol-architect` Skill
3. CTOW ADR
4. CTOW Policy
5. 現有 `.ctow/` governance evidence
6. Repository 現況
7. 使用者本次需求

### 2.1 三條固定操作規則

所有使用情境都先依意圖選擇入口，不因任務大小或緊急程度跳過治理流程：

```text
查詢狀態／接手既有工作 → ctow status
提出全新需求           → ctow-plan "<任務目標>"
啟動已核准 Plan        → ctow-start --plan <PLAN.yaml>
```

1. **查詢時先跑 `ctow status`**：先確認 Orca Runtime、目前 coordinator 綁定的 Run、既有 Run、planning request，以及有效或無效的 Plan。不要根據舊對話、terminal timeout 或 `.ctow/` 檔案猜測執行狀態。
2. **新需求先跑 `ctow-plan`**：它只建立 planning request 與 Sol-ready Prompt，不代表 Plan 已核准，也不建立 Orca Run。
3. **只有核准 Plan 才跑 `ctow-start`**：建議先加 `--dry-run` 驗證。正式執行只建立具權威性的 Orca Run，後續 Task DAG 與 Luna Dispatch 仍由 Terra 負責。

正確：

```bash
ctow status
ctow-plan "新增 API Key 管理"
ctow-guard validate-plan .ctow/plans/PLAN-API-KEYS.yaml
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml --dry-run
ctow-start --plan .ctow/plans/PLAN-API-KEYS.yaml
```

錯誤：

```bash
# 錯誤：新需求尚未經 Sol 規劃與核准，就嘗試開始執行
ctow-start "新增 API Key 管理"

# 錯誤：把 planning request 當成 approved Plan
ctow-start --plan .ctow/requests/PLAN-REQUEST-API-KEYS.yaml
```

`ctow-start "<任務目標>"` 只是 approved Plan 的精確 goal 查找捷徑；找不到唯一且有效的 Plan 時必須拒絕啟動。

### 2.2 情境與第一個指令

| 使用情境 | 第一個指令 | 後續 |
|---|---|---|
| 想知道目前做到哪裡 | `ctow status` | 依 Orca receipt 判讀，不重建狀態 |
| 全新專案或新增功能 | `ctow-plan "<目標>"` | Sol discovery → approved Plan |
| Root cause 未知 Bug | `ctow-plan "調查：<症狀>"` | Sol 定義 hypothesis；必要時規劃 SWARM |
| 已知原因的小型修復 | `ctow-plan "修復：<問題>"` | Sol 可核准 SMALL Plan，但不可跳過 Plan |
| 大型 Refactor | `ctow-plan "重構：<目標與 invariant>"` | 高風險 Work Package 要求獨立審查 |
| Security／Data Integrity | `ctow-plan "<高風險目標>"` | 明列 rollback、audit 與 review gate |
| 已有 approved Plan | `ctow-start --plan <PLAN.yaml> --dry-run` | 預覽通過後才正式 `ctow-start` |

---

## 3. Sol 的固定 Runtime Profile

啟動第一個 Agent 時固定：

```text
Runtime       : Orca → Codex CLI
Model         : GPT-5.6 Sol
Reasoning     : MAX
Fast Mode     : OFF
Access        : Full Access
Approval      : Auto Approval
Role          : Architect
```

Sol 不應在正常 Plan 階段成為主要 coding Agent。

Sol 的價值集中於：

- Requirement interpretation
- Architecture analysis
- Scope definition
- Constraints
- Dependency analysis
- Work Package decomposition
- Risk classification
- Acceptance criteria
- Decision making
- Plan revision
- Final review

---

## 4. 標準專案啟動流程

```text
USER / AGENT
 │
 ├─ 查詢／接手 ─────────────→ ctow status ─→ 判讀 Orca + Governance
 │
 └─ 新需求 ─────────────────→ ctow-plan "<目標>"
                                  │
                                  ▼
                           Planning Request
                                  │
 ▼
SOL
 │
 ├─ Repository Discovery
 ├─ Requirement Analysis
 ├─ Scope / Constraint Analysis
 ├─ Architecture Assessment
 ├─ Risk Identification
 ├─ Acceptance Criteria
 ├─ Work Package Decomposition
 └─ Worker Recommendation
 │
 ▼
CTOW PLAN
 │
 ├─ ctow-guard validate-plan
 ├─ ctow-start --plan <PLAN.yaml> --dry-run
 └─ ctow-start --plan <PLAN.yaml>
 │
 ▼
TERRA
 │
 ├─ Orca Run
 ├─ Task DAG
 ├─ Worker Scheduling
 ├─ Worktree Placement
 └─ Dispatch
 │
 ▼
LUNA Workers
 │
 ├─ Analyze
 ├─ Implement
 ├─ Build
 ├─ Test
 └─ Report
 │
 ▼
TERRA Acceptance / Integration
 │
 ▼
SOL Final Review
 │
 ▼
USER / COMPLETE
```

---

## 5. 通用 Sol 開案 Prompt

```text
你現在是本專案的 CTOW Sol Architect。

請先讀取本 repository 的 AGENTS.md、CTOW Sol Skill、相關 ADR、Policy 與既有 .ctow/ governance evidence，並依 CTOW 現行規範執行。

本次專案目標：

[在這裡填寫需求]

目前先不要進入 implementation。

第一階段請完成：

- repository / system discovery
- requirement interpretation
- scope / out-of-scope
- constraints
- architecture assessment
- dependency analysis
- risk identification
- acceptance criteria
- Work Package decomposition
- dependency DAG
- recommended execution profile
- recommended Luna worker demand
- independent review requirements

若資訊不足：

- 一般工程細節請自行做合理判斷；
- 只有會 materially 改變需求、產品方向、architecture boundary 或 acceptance criteria 的問題才升級給 Human。

禁止在 Plan 階段自行進行正式 implementation。

完成後：

1. 建立正式 CTOW Plan artifact；
2. 驗證 Plan 符合 CTOW Guard / Policy；
3. 依 CTOW hierarchy 將 Approved Plan 交由 Terra；
4. Terra 負責 Orca Run / Task DAG / Luna scheduling；
5. Sol 回到 architecture decision / escalation / final-review 職責。

對執行中升級的問題必須遵循 CTOW Decision Efficiency Policy：

- 使用 canonical issue_fingerprint
- 優先讀既有 Decision Record
- 不得因換措辭而重開問題
- 沒有 material evidence delta 不得反覆驗證
- targeted validation 必須 bounded 且最多一次
- stagnation 後只能 DECIDE / REVISE_PLAN / ESCALATE_HUMAN

現在先從 discovery 與 planning 開始。
```

---

## 6. 情境 A：全新專案

### 情境

例如：建立內部 IT 資產管理平台。

Sol 應優先確認：

- Product boundary
- Core entities
- Authentication / Authorization
- Persistence
- API / UI boundary
- Technology assumptions
- Security
- Operational requirements
- Deployment assumptions
- Acceptance criteria

### 建議 Prompt

```text
請以 CTOW Sol Architect 身份負責本專案。

目標是建立一套內部 IT 資產管理平台，用於管理：
- 電腦
- Server
- Network Device
- User
- Location
- Warranty
- Repair History

目前為全新專案。

第一階段請不要直接 coding。

請先完成：
1. requirement discovery
2. architecture proposal
3. technology assumptions
4. data model
5. security considerations
6. project boundaries
7. Work Package decomposition
8. dependency analysis
9. risk classification
10. acceptance criteria

一般工程細節由你自行合理決定。

只有會直接改變產品方向、架構邊界或重要 acceptance criteria 的問題才需要 Human Decision。

完成後建立正式 CTOW Execution Plan，再依 CTOW hierarchy 交由 Terra 執行。
```

可能的 Plan：

```text
WP-01 Foundation / Project Structure
WP-02 Identity / RBAC
WP-03 Asset Model
WP-04 Inventory API
WP-05 Warranty / Repair
WP-06 Search / Reporting
WP-07 Security / Audit
WP-08 Regression / Acceptance
```

---

## 7. 情境 B：既有專案新增功能

### 情境

例如：現有 Java Server 新增角色交易系統。

這類需求主要風險：

- 既有架構耦合
- Account ownership
- Character ownership
- Inventory consistency
- DB transaction
- Session state
- Rollback
- Concurrency
- Backward compatibility

### 建議 Prompt

```text
請以 CTOW Sol Architect 身份接手目前 repository。

本次需求：
新增角色交易系統。

請先完整理解現有相關架構，包括：
- Character
- Account
- Inventory
- Database persistence
- Login / Session
- Transaction consistency

不要先修改程式碼。

請先分析：
- 現有資料模型
- ownership boundary
- transaction boundary
- concurrency risk
- rollback strategy
- backward compatibility
- 可能受影響的 module
- integration risk

特別限制：
- 不破壞既有登入流程
- 不允許物品複製
- transaction failure 必須 rollback
- 舊角色資料必須相容

請自行決定合理的 Work Package 拆分、dependency 與 worker recommendation。

Plan 完成後依 CTOW hierarchy 交由 Terra 執行。
```

---

## 8. 情境 C：Bug，但 Root Cause 未知

### 情境

例如：玩家登入成功後，偶爾角色列表是空的；重新登入可能恢復。

Sol 不應先假定 root cause，也不應直接修改 production path。

### 建議 Prompt

```text
目前存在 intermittent bug：

玩家登入成功後，偶爾角色列表會回傳空資料；
重新登入後可能恢復。

請以 CTOW Sol Architect 身份接手。

目前不要先假定 root cause，也不要直接修改 production path。

請先：
1. 定義 investigation scope
2. 建立可能 failure domains
3. 建立可證偽 hypothesis
4. 定義每個 hypothesis 所需 evidence
5. 定義成功 / 失敗判準
6. 判斷是否適合使用 CTOW SWARM investigation
7. 產生 investigation Execution Plan

再交由 Terra 調度 Worker。

如果 Worker 發現問題需要 architecture decision，必須依：
- canonical fingerprint
- escalation
- Decision Record
- Decision Progress Ledger
- anti-stagnation policy
逐級處理。
```

可能的 SWARM：

```text
Terra
 ├─ Luna-A → DB / Query Path
 ├─ Luna-B → Session / Concurrency
 └─ Luna-C → Packet / Response Path
```

SWARM 調查期間：

- Luna 彼此不讀 reasoning
- 各自獨立取得證據
- Terra 最後統整
- 不做多數決
- architecture-level conflict 才升 Sol

---

## 9. 情境 D：Root Cause 已知的小型修復

### 情境

例如：`UserService.java` 在 `email == null` 時會 NPE。

### 建議 Prompt

```text
這是一個已定位的小型修復。

問題：
UserService.java 在 email=null 時會發生 NullPointerException。

請以 CTOW Sol Architect 身份快速評估影響範圍。

如果確認：
- scope 小
- root cause 已明確
- 不涉及 architecture change
- 不涉及 shared contract change

則使用 SMALL execution profile 建立最小 Execution Plan。

交由 Terra 使用單一 Luna 完成：
1. root cause confirmation
2. minimal fix
3. regression test
4. required validation

只有風險政策要求時才執行 independent review。

不要把簡單修復過度拆分。
```

理想流程：

```text
Sol
 ↓
Minimal Plan
 ↓
Terra
 ↓
1 Luna
 ↓
Fix + Test
 ↓
Terra Acceptance
 ↓
Sol Final Check
```

---

## 10. 情境 E：大型 Refactor

### 情境

例如：將巨型 Packet Handler switch 拆成 modular handler architecture。

### 建議 Prompt

```text
請以 CTOW Sol Architect 身份規劃 Packet Handler modularization。

目標：
將目前集中式 packet dispatch / giant switch
重構成 modular handler architecture。

限制：
- protocol behavior 不得改變
- opcode mapping 不得改變
- packet order 不得改變
- 必須保留 backward compatibility
- 每一個階段都必須可 build
- 每一個階段都必須可 rollback
- 必須有 regression verification

請先完整分析：
- dispatcher
- handler dependencies
- shared state
- initialization order
- protocol contract
- error handling
- test coverage

產生漸進式 Execution Plan。

High-risk Work Package 必須要求 independent Luna review。

Plan 完成後交由 Terra 排程。
Sol 不應自行進入主要 implementation loop。
```

---

## 11. 情境 F：使用者已有方案，但不是正式決策

例如：

> 我傾向使用 Redis 做 distributed session。

建議：

```text
我目前傾向使用 Redis 做 distributed session。

這只是 proposed direction，不是已核准 architecture decision。

請 Sol 在 Plan 階段獨立驗證：
- 是否真的需要 distributed session
- Redis 是否符合需求
- consistency model
- failure mode
- operational complexity
- latency impact
- 是否有更簡單方案

如果分析支持 Redis，納入 Plan。

如果不支持，請提出替代方案、trade-off 與 evidence。

不要因為這是使用者提出的方案就直接視為 architecture requirement。
```

---

## 12. 情境 G：已有完整規格

如果已有：

- PRD
- Protocol Specification
- DB Schema
- Acceptance Criteria
- API Contract

建議：

```text
以下文件為 authoritative requirements：

- PRD.md
- PROTOCOL-SPEC.md
- DATABASE-SCHEMA.md
- ACCEPTANCE.md

Sol 不得自行修改 requirement intent。

請針對目前 repository 與上述規格：
1. 做 gap analysis
2. 建立 implementation architecture
3. 找出 requirement / implementation conflict
4. 建立 Work Package
5. 建立 dependency DAG
6. 定義風險與 independent review requirement
7. 產生正式 Execution Plan

只有當：
- 規格內部矛盾
- 規格與現有架構無法同時成立
- acceptance criteria 無法同時滿足

才建立 Human Decision Request。
```

---

## 13. 情境 H：高風險 Security / Data Integrity 變更

適用：

- Authentication
- Authorization
- Billing
- Financial transaction
- Encryption
- Database migration
- Inventory ownership
- Account transfer

建議要求：

```text
本次變更屬於 high-risk。

請 Plan 強制：
- independent review
- rollback strategy
- regression test
- security / integrity acceptance criteria
- failure mode analysis
- auditability

任何 architecture conflict 必須使用正式 escalation，
不得由 Luna 或 Terra 偷偷 workaround。
```

---

## 14. Sol 何時應詢問 Human？

### 不需要 Human

一般工程細節，例如：

- method name
- class split
- internal helper design
- test fixture structure
- logging format
- minor package placement
- local refactor technique

### 應建立 Human Decision

例如：

- 是否保留 legacy protocol
- 是否允許 breaking API change
- 是否放棄 backward compatibility
- 是否擴張 project scope
- 是否接受 migration risk
- 是否改變產品行為
- 是否改變 authoritative requirement
- 兩個方案都合理，但 trade-off 本質上是產品/商業決策

---

## 15. 問題上報流程

```text
Luna
  │
  │ escalation
  ▼
Terra
  │
  ├─ execution-level → Terra 解決
  │
  └─ architecture / plan-level
          │
          ▼
         Sol
```

原則：

- Luna 不直接越級到 Sol
- Sol 不直接跳過 Terra 管理 Luna
- Terra 是 escalation compressor / deduplicator

---

## 16. Anti-Stagnation：避免 Sol 無意義反覆驗證

核心原則：

> **No new evidence, no new loop.**

問題到 Sol 前，Terra 必須：

1. 建立 canonical `issue_fingerprint`
2. 查既有 Decision Record
3. 查既有 Decision Progress Ledger
4. 去除重複 evidence
5. 標記 falsified hypotheses
6. 判斷是否有 material evidence delta
7. 提供 precise decision question

Sol 不應重新讀取整份 Worker transcript 來重新調查同一件事。

---

## 17. Sol 面對 Escalation 時允許的四種 Progress Action

```text
DECIDE

REQUEST_TARGETED_EVIDENCE

REVISE_PLAN

ESCALATE_HUMAN
```

禁止：

```text
再全面 review 一次
再找另一個 Luna 看一次
再掃一次 repo
再跑一次同樣測試
換句話重新問問題
```

沒有新的 information gain 就不算 progress。

---

## 18. Targeted Validation

若 Sol 確實缺一個會改變決策的關鍵證據，可使用：

```text
REQUEST_TARGETED_EVIDENCE
```

但必須限定：

```yaml
hypothesis:
method:
success_criterion:
failure_criterion:
expected_decision_impact:
max_attempts: 1
```

例如：

```yaml
hypothesis:
  local compatibility adapter 可以保留 reconnect behavior。

method:
  建立 disposable worktree，只實作最小 POC 並執行 reconnect regression。

success_criterion:
  所有 reconnect tests 通過。

failure_criterion:
  任一 regression fail，或需要 public API change。

expected_decision_impact:
  success -> 保留原 Plan
  failure -> revise Plan

max_attempts: 1
```

---

## 19. Stagnation 觸發條件

若：

```text
same canonical fingerprint
+
same decision_question_key
+
cycle_count >= 2
+
no material evidence delta
```

則：

```text
stagnation_detected = true
```

此時只能：

```text
DECIDE
REVISE_PLAN
ESCALATE_HUMAN
```

不能再次 `REQUEST_TARGETED_EVIDENCE`。

---

## 20. Human 也不要破壞 Anti-Loop

如果 Sol 問：

> 要不要再讓 Luna 確認一次？

但目前沒有 material evidence delta，不建議回答：

```text
可以，再確認。
```

應回：

```text
依 CTOW Decision Efficiency Policy 處理。

若目前沒有 material evidence delta，
不得再執行同類型驗證。

請選擇：
- DECIDE
- REVISE_PLAN
- ESCALATE_HUMAN
```

---

## 21. Execution Profiles

### SMALL

適合：

- 已定位 Bug
- 小功能
- 單一 module
- 低依賴
- 低風險

```text
Sol → Terra → Luna ×1
```

### MEDIUM

適合：

- 跨 2~3 module
- 有 dependency
- 需要 parallel work
- 中等 regression risk

```text
Sol → Terra → Luna ×2
```

### FULL

適合：

- 大型 feature
- 大型 refactor
- 多 Work Package
- 高風險 integration

```text
Sol → Terra → Luna ×3
```

### SWARM

適合：

- Root cause 不明
- concurrency
- intermittent bug
- complex regression
- architecture anomaly

```text
             Terra
               │
     ┌─────────┼─────────┐
     ▼         ▼         ▼
  Luna-A    Luna-B    Luna-C
Independent Independent Independent
     │         │         │
     └─────────┼─────────┘
               ▼
         Terra Synthesis
               │
        ┌──────┴──────┐
        ▼             ▼
    Converged       Conflict
        │             │
        ▼             ▼
     Execute          Sol
```

---

## 22. Independent Review

High / Critical risk：

```text
Luna-A
Implementation
   │
   ▼
Worker Report
   │
   ▼
Luna-B
Independent Review
```

必須符合：

```text
author_agent != reviewer_agent
author_session != reviewer_session
author_dispatch != reviewer_dispatch
```

Reviewer 初始優先取得：

- Task Contract
- Acceptance Criteria
- Diff
- Test Results
- Repository Evidence

不先取得 author 完整 reasoning transcript。

---

## 23. 使用者不應直接繞過 hierarchy

不建議：

```text
User → Luna-A
User → Luna-B
User → Terra
```

直接發散下命令。

否則可能造成：

- Terra 排程失真
- Sol Plan authority 被破壞
- Task DAG 被繞過
- File ownership 衝突
- Decision Record 不完整

正常入口：

```text
USER → SOL
```

Human intervention 限於：

- Human Decision
- Break-glass
- Scope Change
- Final Sign-off

---

## 24. 理想的人機互動方式

不理想：

```text
幫我改 A
再改 B
這個錯了
再看 C
重跑 test
再 review 一次
```

理想：

```text
我要完成 X。

需求：
...

限制：
...

不可改：
...

驗收：
...

請 Sol 接案。
```

之後：

```text
USER
 │
 ▼
SOL
WHAT / WHY
 │
 ▼
PLAN
 │
 ▼
TERRA
WHO / WHEN / ORDER
 │
 ▼
TASK DAG
 │
 ▼
LUNA
HOW
 │
 ▼
CODE / TEST / REPORT
```

---

## 25. 建議開案資訊模板

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

不必每一項都填。

---

## 26. 完整範例：新增 API Key 管理

User：

```text
你現在是本專案的 CTOW Sol Architect。

本次需求：
新增 API Key 管理功能。

背景：
目前系統只有 username/password login。

目標：
允許 Admin 為 integration service 建立 API Key，
並支援 revoke、expiration 與 scope。

限制：
- 不改現有 login behavior
- API Key 不得明文保存
- revoke 後必須立即失效
- 必須留下 audit log
- 既有 API backward compatible

請先進行 discovery 與 planning。
不要直接 implementation。

完成正式 Plan 後依 CTOW hierarchy 交 Terra 執行。
```

Sol 可能建立：

```text
WP-01 Existing Auth Discovery
WP-02 API Key Data Model
WP-03 Key Authentication Path
WP-04 Scope Enforcement
WP-05 Revocation / Expiry
WP-06 Audit
WP-07 Security / Regression
```

Terra 再依 dependency 與 Worker capacity 做實際排程。

---

## 27. 完整範例：執行中發生 Architecture Conflict

Luna 發現：

```text
現有 middleware 在 credential validation 後會 cache identity 5 分鐘。

這與 revoke 後立即失效 requirement 衝突。
```

Luna → Terra：

```yaml
severity: high
blocking: true

problem:
  identity cache TTL conflicts with immediate API-key revocation.

evidence:
  - AuthMiddleware
  - IdentityCache
  - revoke acceptance criteria

decision_required:
  change cache invalidation architecture or relax immediate revocation.
```

Terra canonicalize：

```text
auth-cache-immediate-revocation
```

查 `.ctow/decisions/`。

若沒有歷史 decision，再送 Decision Brief 給 Sol。

Sol 不應重新掃整個 auth repository，而應針對 compressed evidence：

- DECIDE
- REQUEST_TARGETED_EVIDENCE（若真的缺關鍵證據）
- REVISE_PLAN
- ESCALATE_HUMAN

---

## 28. 完整範例：Stagnation

第一輪：

```text
issue_fingerprint:
auth-cache-immediate-revocation

Sol:
REQUEST_TARGETED_EVIDENCE
```

Luna 執行一次 bounded POC。

結果：

```text
無法在現有 cache architecture 下保證立即 revoke，
除非增加 explicit invalidation path。
```

第二輪：

```text
same fingerprint
same decision_question_key
cycle_count: 2
```

如果沒有新的 material delta：

```text
stagnation_detected: true
```

Sol 必須：

```text
DECIDE:
增加 invalidation architecture

或

REVISE_PLAN:
修改 authentication architecture

或

ESCALATE_HUMAN:
詢問是否允許 revoke 最長延遲 5 分鐘
```

不能再找第三個 Luna 重驗同一問題。

---

## 29. 專案完成

所有 Work Package：

```text
Execution Completed
Independent Review Passed
Integration Passed
Acceptance Passed
```

Terra整理執行結果。

Sol執行：

- Final Architecture Review
- Plan Compliance Review
- Residual Risk Review
- Acceptance Criteria Review

最後：

```text
SOL SIGN-OFF
 ↓
USER
```

User 應得到：

- 完成內容
- 重大 Architecture Decision
- Residual Risks
- Test / Review Results
- Deferred Items
- Acceptance Criteria 結果

---

## 30. 最終操作心法

你不需要管理每個 Agent。

理想用法：

```text
你：
「我要完成 X。
這是 requirement、constraint 與 acceptance criteria。
Sol 接案。」
```

接著：

```text
Sol 想方向
Terra 管工程
Luna 做工程
```

只有真正涉及：

- 產品決策
- Architecture trade-off
- Scope Change
- Breaking Change
- 重大風險接受

才重新回到 Human。

---

## 31. 一句話版

```text
User 定義「要什麼」
Sol 決定「應該怎麼做」
Terra 決定「誰、何時、按什麼順序做」
Luna 負責「把它真的做完」
Orca 負責「讓整個執行生命週期真的跑起來」
CTOW 負責「確保所有 Agent 不越權、不失控、不原地燒 token」
```
