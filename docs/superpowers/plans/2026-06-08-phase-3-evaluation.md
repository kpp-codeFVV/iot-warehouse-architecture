# Phase 3 Architecture Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the Phase 3 architecture evaluation package for the IoT smart warehouse project.

**Architecture:** This phase evaluates the accepted edge-cloud collaborative architecture using a lightweight ATAM process. The documents connect quality scenarios, ADRs, views, sensitivity points, tradeoffs, risks, and technical debt so later PoC and prototype work can target the highest-risk assumptions.

**Tech Stack:** Markdown, ATAM-style evaluation tables, Git, PowerShell verification commands.

---

## File Structure

- Create: `docs/04_evaluation/ATAM_Record.md` - lightweight ATAM evaluation record.
- Create: `docs/04_evaluation/Sensitivity_Tradeoff.md` - sensitivity point and tradeoff point analysis.
- Create: `docs/04_evaluation/Risk_List.md` - risk list and action items.
- Create: `docs/04_evaluation/Tech_Debt.md` - technical debt register.

## Task 1: Write ATAM Record

**Files:**
- Create: `docs/04_evaluation/ATAM_Record.md`

- [ ] **Step 1: Create ATAM record**

Write a lightweight ATAM document with these exact sections:

- `## 1. 评估范围与目标`
- `## 2. 业务驱动因素回顾`
- `## 3. 架构描述`
- `## 4. 质量属性效用树`
- `## 5. 架构方法分析`
- `## 6. 敏感点清单`
- `## 7. 权衡点清单`
- `## 8. 风险与非风险`
- `## 9. 评估结论`

The document must reference Phase 1 QAS IDs, Phase 2 ADR IDs, and Phase 2 view files.

- [ ] **Step 2: Verify ATAM sections**

Run:

```powershell
$content = Get-Content 'docs/04_evaluation/ATAM_Record.md' -Raw -Encoding utf8
$sections = @(
  '## 1. 评估范围与目标',
  '## 2. 业务驱动因素回顾',
  '## 3. 架构描述',
  '## 4. 质量属性效用树',
  '## 5. 架构方法分析',
  '## 6. 敏感点清单',
  '## 7. 权衡点清单',
  '## 8. 风险与非风险',
  '## 9. 评估结论'
)
$missing = $sections | Where-Object { -not $content.Contains($_) }
if ($missing) {
  $missing
  exit 1
}
'atam sections ok'
```

Expected: prints `atam sections ok`.

- [ ] **Step 3: Commit ATAM record**

Run:

```powershell
git add docs/04_evaluation/ATAM_Record.md
git commit -m "docs: add ATAM evaluation record"
```

Expected: Git creates a commit named `docs: add ATAM evaluation record`.

## Task 2: Write Sensitivity and Tradeoff Analysis

**Files:**
- Create: `docs/04_evaluation/Sensitivity_Tradeoff.md`

- [ ] **Step 1: Create sensitivity and tradeoff document**

Write a document with:

- A sensitivity point table with IDs `SP-001` through `SP-008`.
- A tradeoff point table with IDs `TP-001` through `TP-006`.
- A decision impact matrix linking sensitivity/tradeoff IDs to ADRs and QAS IDs.
- A verification focus section explaining which points should be validated in Phase 4.

- [ ] **Step 2: Verify sensitivity and tradeoff counts**

Run:

```powershell
$spCount = (Select-String -Path 'docs/04_evaluation/Sensitivity_Tradeoff.md' -Pattern '^\| SP-' -Encoding utf8 | Measure-Object).Count
$tpCount = (Select-String -Path 'docs/04_evaluation/Sensitivity_Tradeoff.md' -Pattern '^\| TP-' -Encoding utf8 | Measure-Object).Count
if ($spCount -lt 8) {
  "sensitivity count $spCount below 8"
  exit 1
}
if ($tpCount -lt 6) {
  "tradeoff count $tpCount below 6"
  exit 1
}
"sensitivity and tradeoff ok: SP=$spCount TP=$tpCount"
```

Expected: prints `sensitivity and tradeoff ok: SP=8 TP=6`.

- [ ] **Step 3: Commit sensitivity and tradeoff analysis**

Run:

```powershell
git add docs/04_evaluation/Sensitivity_Tradeoff.md
git commit -m "docs: add sensitivity and tradeoff analysis"
```

Expected: Git creates a commit named `docs: add sensitivity and tradeoff analysis`.

## Task 3: Write Risk List

**Files:**
- Create: `docs/04_evaluation/Risk_List.md`

- [ ] **Step 1: Create risk list**

Write a risk register with:

- At least 10 risks with IDs `RISK-001` through `RISK-010`.
- Columns: 风险ID, 描述, 风险等级, 影响的质量属性, 缓解策略, 行动项, 负责角色, 截止阶段.
- A risk priority summary.
- A Phase 4 validation mapping that identifies risks requiring PoC, load test, or fault injection.

- [ ] **Step 2: Verify risk count**

Run:

```powershell
$riskCount = (Select-String -Path 'docs/04_evaluation/Risk_List.md' -Pattern '^\| RISK-' -Encoding utf8 | Measure-Object).Count
if ($riskCount -lt 10) {
  "risk count $riskCount below 10"
  exit 1
}
"risks ok: $riskCount"
```

Expected: prints `risks ok: 10` or higher.

- [ ] **Step 3: Commit risk list**

Run:

```powershell
git add docs/04_evaluation/Risk_List.md
git commit -m "docs: add architecture risk list"
```

Expected: Git creates a commit named `docs: add architecture risk list`.

## Task 4: Write Technical Debt Register

**Files:**
- Create: `docs/04_evaluation/Tech_Debt.md`

- [ ] **Step 1: Create technical debt register**

Write a technical debt register with:

- At least 8 debt items with IDs `DEBT-001` through `DEBT-008`.
- Columns: 债务ID, 描述, 关联ADR, 债务类型, 影响范围, 偿还策略, 优先级.
- A repayment roadmap grouped into short-term, medium-term, and long-term actions.

- [ ] **Step 2: Verify debt count**

Run:

```powershell
$debtCount = (Select-String -Path 'docs/04_evaluation/Tech_Debt.md' -Pattern '^\| DEBT-' -Encoding utf8 | Measure-Object).Count
if ($debtCount -lt 8) {
  "debt count $debtCount below 8"
  exit 1
}
"tech debt ok: $debtCount"
```

Expected: prints `tech debt ok: 8` or higher.

- [ ] **Step 3: Commit technical debt register**

Run:

```powershell
git add docs/04_evaluation/Tech_Debt.md
git commit -m "docs: add technical debt register"
```

Expected: Git creates a commit named `docs: add technical debt register`.

## Task 5: Cross-Document Verification

**Files:**
- Review: `docs/04_evaluation/ATAM_Record.md`
- Review: `docs/04_evaluation/Sensitivity_Tradeoff.md`
- Review: `docs/04_evaluation/Risk_List.md`
- Review: `docs/04_evaluation/Tech_Debt.md`

- [ ] **Step 1: Verify required Phase 3 files exist**

Run:

```powershell
$files = @(
  'docs/04_evaluation/ATAM_Record.md',
  'docs/04_evaluation/Sensitivity_Tradeoff.md',
  'docs/04_evaluation/Risk_List.md',
  'docs/04_evaluation/Tech_Debt.md'
)
foreach ($file in $files) {
  if (-not (Test-Path $file)) {
    "$file missing"
    exit 1
  }
}
'phase 3 files ok'
```

Expected: prints `phase 3 files ok`.

- [ ] **Step 2: Verify traceability keywords**

Run:

```powershell
$content = (Get-ChildItem 'docs/04_evaluation' -Filter '*.md' -Recurse | ForEach-Object { Get-Content $_.FullName -Raw -Encoding utf8 }) -join "`n"
$terms = @('QAS-001','QAS-003','ADR-001','ADR-006','MQTT','边云协同','TimescaleDB','设备影子','事件驱动','边缘缓存')
foreach ($term in $terms) {
  if ($content -notlike "*$term*") {
    "missing $term"
    exit 1
  }
}
'phase 3 traceability ok'
```

Expected: prints `phase 3 traceability ok`.

- [ ] **Step 3: Verify no unresolved placeholders**

Run:

```powershell
$files = Get-ChildItem 'docs/04_evaluation' -Filter '*.md' -Recurse
$patterns = @('TO' + 'DO', 'TB' + 'D', '待' + '定', '占' + '位', 'x' + 'x' + 'x', 'X' + 'X' + 'X')
foreach ($pattern in $patterns) {
  $matches = $files | Select-String -Pattern $pattern -CaseSensitive:$false -Encoding utf8
  if ($matches) {
    $matches
    exit 1
  }
}
'phase 3 no placeholders ok'
```

Expected: prints `phase 3 no placeholders ok`.

- [ ] **Step 4: Inspect Git status**

Run:

```powershell
git status --short --ignored
```

Expected: only the assignment PDF should be untracked and `.superpowers/` should be ignored.

## Self-Review Notes

- Spec coverage: This plan covers every Phase 3 file required by the assignment PDF: ATAM record, sensitivity/tradeoff analysis, risk list, and technical debt register.
- Placeholder scan: The plan contains no unresolved placeholder instructions.
- Type consistency: QAS IDs, ADR IDs, service names, and Phase 4 validation targets match the existing Phase 1 and Phase 2 documents.
